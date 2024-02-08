#!/bin/bash
set -eExuo pipefail

set +u
SCOPE="$1"
set -u

if [ "$SCOPE" == "--scope=ci-cd" ]; then
    FILE_ARTIFACTS="$(realpath variables.env)"
fi

cd "$(realpath "$(dirname "$0")")"/..

if [ "$SCOPE" == "--scope=ci-cd" ]; then
    pip install https://download.splunk.com/misc/packaging-toolkit/splunk-packaging-toolkit-1.0.1.tar.gz
    pip install splunk-appinspect
    find . -type f -print -exec chmod o-wx {} \;
fi

splunk-appinspect inspect security_saved_searches --mode precert --included-tags cloud
slim package security_saved_searches -o app

cd app
APP_FILENAME="$(ls -1 *.tar.gz | sort | tail -n 1)"
APP_PATH="$(realpath "$APP_FILENAME")"
APP_VERSION="$(echo "$APP_FILENAME"  | sed -E "s/^.*-(.*).tar.gz/\1/")"

if [ "$SCOPE" == "--scope=ci-cd" ]; then
    echo "TAG=v$APP_VERSION" >> "$FILE_ARTIFACTS"
    echo "PACKAGE_VERSION=$APP_VERSION" >> "$FILE_ARTIFACTS"
    echo "SPLUNK_APP_ASSET_NAME=$APP_FILENAME" >> "$FILE_ARTIFACTS"
    echo "SPLUNK_APP_ASSET=$APP_PATH" >> "$FILE_ARTIFACTS"
fi
