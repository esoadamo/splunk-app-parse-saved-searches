# WANRING: Development-only script, requires a manual setup first
python .\utils\bump-app-version.py
wsl /snap/bin/docker exec -it p39 bash /projects/splunk-app-parse-saved-searches/utils/package-splunk-app.bash