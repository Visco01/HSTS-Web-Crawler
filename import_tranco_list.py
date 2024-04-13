#!/usr/bin/env python3
from tranco import Tranco
import time
import sqlite3
from playwright.sync_api import sync_playwright

start = time.time()

t = Tranco(cache=True, cache_dir='.tranco')
latest_list = t.list()

conn = sqlite3.connect('tranco_sites.sqlite')
c = conn.cursor()

c.execute('''DROP TABLE IF EXISTS sites''')
c.execute('''CREATE TABLE IF NOT EXISTS sites
             (rank INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, HSTS BOOLEAN, max_age INTEGER, include_subdomains BOOLEAN, preload BOOLEAN)''')

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    for domain in latest_list.top(10):
        url = "http://www." + domain if not domain.startswith("www.") else domain
        try:
            response = page.goto(url)
            hs = response.headers.get("strict-transport-security")
            hs_array = hs.split("; ") if hs is not None else None
            print(hs_array)
        except Exception as e:
            print(f"Error collecting HSTS policy for {domain}: {e}")
        c.execute("INSERT INTO sites (url, HSTS, max_age, include_subdomains, preload) VALUES (?, ?, ?, ?, ?)",
        (url,
         hs is not None,
         int(hs_array[0].split("=")[1]) if hs is not None else None,
         "includeSubdomains" in hs_array if hs is not None else False,
         "preload" in hs_array if hs is not None else False,))
        hs = None

# Commit changes and close the connection
conn.commit()
conn.close()

end = time.time()
print(f"Time elapsed: {end - start} seconds")
