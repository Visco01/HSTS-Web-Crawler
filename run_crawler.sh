#!/usr/bin/env sh

# Run commands in parallel
python3 hsts_web_crawler.py firefox &
python3 hsts_web_crawler.py chromium &

# Wait for all background processes to finish
wait
