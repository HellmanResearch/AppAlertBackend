#!/usr/bin/env bash
nohup ../venv/bin/python3 exporter/exporter.py >> exporter/stdout.log 2>&1 &