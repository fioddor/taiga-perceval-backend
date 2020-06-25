#!/bin/bash
#
# Purpose: Run Perceval with Taiga Backend.
#
# Usage..: 1) Adjust project and categories to be retrieved.
#          2) Provide your token as first argument in the call.
#          3) Read the output files.
#

URL=https://api.taiga.io/api/v1/
TKN=$1

PRJ=156665

ask_taiga() {
    perceval taiga --category $2 --url $URL -t $TKN --no-archive --json-line $1 -o p$1.$2.perceval.json
}

ask_taiga $PRJ basics
ask_taiga $PRJ stats
ask_taiga $PRJ issues_stats
ask_taiga $PRJ epics
ask_taiga $PRJ userstories
ask_taiga $PRJ tasks
ask_taiga $PRJ wiki

ls -l p*.perceval.scr

echo Done!

