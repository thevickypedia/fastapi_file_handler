#!/usr/bin/env bash
# 'set -e' stops the execution of a script if a command or pipeline has an error.
# This is the opposite of the default shell behaviour, which is to ignore errors in scripts.
set -e

rm -rf docs
mkdir docs
mkdir -p doc_generator/_static  # Creates a _static folder if unavailable
[ -z "$PASSWORD" ] && export PASSWORD="None"  # Sets the PASSWORD env var if unavailable
cp README.md doc_generator && cd doc_generator && make clean html && mv _build/html/* ../docs && rm README.md
if [[ $PASSWORD == "None" ]] ; then unset PASSWORD; else :; fi  # Unsets PASSWORD env var, if it was set by this script
touch ../docs/.nojekyll
