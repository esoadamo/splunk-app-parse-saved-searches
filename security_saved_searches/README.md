# Parse security saved searches from records

## Motivation

In many cases, there is a need for a bulk import of saved searches into a Splunk.
This application streamlines this process by reducing the creation of said searches
to only pushing data to a Splunk index/input lookup and then processing it with
this application.

## Description

The `gensecsavsearch` command returns events with 

## Example

With having a input lookup `stored_searches`, having columns:
- `name`
- `cron`
- `enabled` (yes/no)

```text
  | inputlookup stored_searches
  | gensecsavsearch
```

Or, with enabled verbose logging:

```text
  | inputlookup stored_searches
  | gensecsavsearch verbose=yes
```

## Issue Reporting

[Github @ esoadamo/splunk-parse_saved-searches-app](https://github.com/esoadamo/splunk-app-parse-saved-searches)