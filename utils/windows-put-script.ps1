# WANRING: Development-only script, requires a manual setup first
Get-Content .\security_saved_searches\bin\generate_saved_searches.py |
    wsl /snap/bin/docker  exec -i -u root splunk bash -c 'cat > /opt/splunk/etc/apps/security_saved_searches/bin/generate_saved_searches.py'
