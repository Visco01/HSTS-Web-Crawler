#!/usr/bin/env sh
pip install -r requirements.txt
python3 hsts_web_crawler.py webkit
python3 hsts_web_crawler.py firefox
python3 hsts_web_crawler.py chromium
