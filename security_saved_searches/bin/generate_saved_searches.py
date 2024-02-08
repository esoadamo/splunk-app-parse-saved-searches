import os, sys
from typing import Dict, List, Set
try:
    from typing import TypedDict
except ImportError:
    TypedDict = Dict
    pass  # Splunk is using too old Python version

DEBUG = False
APP = "security_saved_searches"

def joblog(*args, log_lines = [], **kwargs):
    if not DEBUG:
        return
    if args:
        log_lines.append(' '.join(map(lambda x: str(x), args)))
        print("[GS]", *args, file=sys.stderr, **kwargs)
    return log_lines


joblog("Opened")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.searchcommands import (
    StreamingCommand,
    Configuration,
    Option,
    dispatch
)
from splunklib.client import SavedSearch


class SearchRecord(TypedDict):
    id: str
    name: str
    cron: str
    search: str
    enabled: bool


@Configuration()
class ParsSecuritySavedSearchesCommand(StreamingCommand):
    verbose = Option(
        doc='''
        **Syntax:** **verbose=***yes*
        **Description:** Allow logging of verbose logs''',
        require=False
    )

    def stream_safe(self, records):
        if self.verbose and self.verbose.lower() == "yes":
            global DEBUG
            DEBUG = True

        saved_searches = self.service.saved_searches
        
        existing_searches_names: Set[str] = set()

        joblog("Existing saved searches")
        for current_search in saved_searches.list(app=APP):
            existing_searches_names.add(current_search.name)
        joblog("-- " + ', '.join(existing_searches_names))

        new_searches_records: Dict[str, SearchRecord] = {}

        joblog("Parse records")
        for new_record in records:
            search_name = new_record['name']
            search_cron = new_record['cron']
            search_search = new_record['search']
            search_enabled = new_record['enabled'].lower() == "yes"

            new_search_record = next(self.output_record(
                name=search_name,
                cron=search_cron,
                search=search_search,
                enabled=search_enabled
            ))
            new_searches_records[new_search_record["name"]] = new_search_record
            yield new_search_record

            if search_name not in existing_searches_names:
                joblog(f"-- creating search {search_name}")
                saved_searches.create(
                    name=search_name,
                    search=search_search
                )
            else:
                joblog(f"-- search {search_name} already exists")
        
        existing_searches: List[SavedSearch] = saved_searches.list(app=APP)
        searches_to_remove_names: Set[str] = set()

        joblog("Sync searches")
        for current_search in existing_searches:
            joblog(f"- processing {current_search.name}")
            new_record = new_searches_records.get(current_search.name)
            if new_record is None:
                joblog(f"-- scheduled to be removed")
                searches_to_remove_names.add(current_search.name)
                continue

            content = current_search.content
            search_search = current_search["search"]
            search_enabled = not bool(int(content["disabled"]))
            search_scheduled = bool(int(content["is_scheduled"]))
            cron_schedule = content["cron_schedule"]

            if new_record["enabled"] != search_enabled:
                if new_record["enabled"]:
                    joblog("-- enabling")
                    current_search.enable()
                else:
                    joblog("-- disabling")
                    current_search.disable()

            if search_search != new_record["search"]:
                joblog("-- updating search")
                current_search.update(search=new_record["search"])

            if cron_schedule != new_record["cron"]:
                joblog("-- updating cron")
                current_search.update(
                    cron_schedule=new_record["cron"]
                
                )
                
            if new_record["enabled"] != search_scheduled:
                if new_record["enabled"]:
                    joblog("-- enabling schedule")
                    current_search.update(
                        is_scheduled=True
                    )
                else:
                    joblog("-- disabling schedule")
                    current_search.update(
                        is_scheduled=False
                    )

        if searches_to_remove_names:
            joblog("Deleting old searches")
            for search_name in searches_to_remove_names:
                saved_searches.delete(name=search_name, app=APP)

        joblog("All done")


    def stream(self, records):
        joblog("Starting safe stream")
        try:
            yield from self.stream_safe(records)
            joblog("No error occured")
        except Exception:
            joblog("An error occured")
            if DEBUG:
                import traceback
                joblog(traceback.format_exc())
            else:
                raise

        if DEBUG:
            for line in joblog():
                yield from self.output_record(debug_log=line)

    def output_record(self, **kwargs):
        keys = ["name", "cron", "search", "enabled"] + ([] if not DEBUG else ["debug_log"])
        
        data = {key: kwargs.get(key, "") for key in keys}
        
        if "debug_log" in keys and "debug_log" not in data:
            try:
                data["debug_log"] = joblog().pop(0)
            except IndexError:
                pass
        
        yield data

joblog("Loaded")
dispatch(ParsSecuritySavedSearchesCommand, sys.argv, sys.stdin, sys.stdout, __name__)
joblog("Dispatched")
