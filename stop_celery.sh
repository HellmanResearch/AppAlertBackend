#!/usr/bin/env bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ../venv/bin/celery multi stop alert -A AppAlertBackend -B --pidfile="./%n.pid" --logfile="./logs/%n%I.log" -l debug --concurrency=8
elif [[ "$OSTYPE" == "darwin"* ]]; then
    celery multi stop alert -A AppAlertBackend -B --pidfile="./%n.pid" --logfile="./logs/%n%I.log" -l debug --concurrency=8
fi

ps -ef | grep 'celery -A AppAlertBackend' | grep -v grep | awk '{print $2}' | xargs kill -9
echo stopped
