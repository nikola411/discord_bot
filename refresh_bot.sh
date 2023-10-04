#!/bin/bash
GIT_MESSAGE=`git pull`
if [[ "Already up to date." != "$GIT_MESSAGE" ]]; then
    PID=`ps -eaf | grep 'python3 main.py' | grep -v grep | awk '{print $2}'`
    if [[ "" !=  "$PID" ]]; then
        echo "killing $PID"
        kill -9 $PID
    fi
    nohup python3 main.py &
    echo Refresh done!
fi
