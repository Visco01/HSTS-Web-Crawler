#!/usr/bin/env python3
from tranco import Tranco
import sqlite3

# Initialize Tranco object
t = Tranco(cache=True, cache_dir='.tranco')

# Retrieve the latest Tranco list
latest_list = t.list()

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('tranco_sites.sqlite')
c = conn.cursor()

c.execute('''DROP TABLE IF EXISTS sites''')

# Create table to store site information
c.execute('''CREATE TABLE IF NOT EXISTS sites
             (rank INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT)''')

print(latest_list.top(10))
# Insert top 10,000 sites into the database
for domain in latest_list.top(10000):
    print(domain)
    c.execute("INSERT INTO sites (domain) VALUES (?)", (domain,))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Top 10,000 sites have been inserted into the SQLite database.")
