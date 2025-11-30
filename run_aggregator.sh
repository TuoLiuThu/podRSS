#!/bin/bash
cd "$(dirname "$0")"
source .env
# If using a virtual environment, activate it here
# source venv/bin/activate
python3 podcast_aggregator.py
