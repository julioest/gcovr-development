#!/bin/bash

# This script will "rebuild" html files based on the templates.

set -xe

export REPONAME="json"
export ORGANIZATION="boostorg"
GCOVRFILTER=".*/$REPONAME/.*"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/$REPONAME"
BOOST_CI_SRC_FOLDER=$(pwd)

outputlocation="$BOOST_CI_SRC_FOLDER/gcovr"
rm -rf $outputlocation || true
mkdir -p $outputlocation

cd ../boost-root
gcovr --merge-mode-functions separate -p \
    --merge-lines \
    --html-nested \
    --html-template-dir=../templates/html \
    --exclude-unreachable-branches \
    --exclude-throw-branches \
    --exclude '.*/test/.*' \
    --exclude '.*/extra/.*' \
    --filter "$GCOVRFILTER" \
    --html \
    --output "$outputlocation/index.html"

# Generate tree.json for sidebar navigation
python3 "../scripts/build_tree.py" "$outputlocation"
