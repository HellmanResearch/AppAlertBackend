#!/usr/bin/env bash
export IS_CELERY=1
export PROMETHEUS_MULTIPROC_DIR=prometheus_multiproc_dir
args='multi start alert -A AppAlertBackend -B --pidfile="./%n.pid" --logfile="./logs/%n%I.log" -l debug --concurrency=8'
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ../venv/bin/celery $args
elif [[ "$OSTYPE" == "darwin"* ]]; then
    celery $args
fi