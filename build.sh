#!/bin/bash

# This script will "rebuild" html files based on the templates.

set -xe

export REPONAME="json"
export ORGANIZATION="boostorg"
GCOVRFILTER=".*/$REPONAME/.*"

cd "$REPONAME"
BOOST_CI_SRC_FOLDER=$(pwd)

rm -rf "gcovr/*"
cd ../boost-root

# To copy files to the main Windows disk:
# mkdir -p /mnt/c/output

outputlocation="$BOOST_CI_SRC_FOLDER/gcovr/index.html"
outputlocation="/mnt/c/output/index.html"

gcovr --merge-mode-functions separate -p --html-nested --html-template-dir=..\templates --exclude-unreachable-branches --exclude-throw-branches --exclude '.*/test/.*' --exclude '.*/extra/.*' --filter "$GCOVRFILTER" --html --output "$outputlocation"
