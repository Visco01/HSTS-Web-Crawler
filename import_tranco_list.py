from tranco import Tranco
import time
import sqlite3
import re
from playwright.sync_api import sync_playwright
import matplotlib.pyplot as plt

max_age_regex = r'\bmax-age=[0-9]+\b'
include_subdomains_regex = "includeSubdomains"
preload_regex = "preload"

def fetch_hsts_policy(url, page):
    try:
        response = page.goto(url)
        hs = response.headers.get("strict-transport-security")
        hs_array = hs.split(";") if hs is not None else None
        return hs_array
    except Exception as e:
        # print(f"Error collecting HSTS policy for {url}: {e}")
        return None

def create_database_table(cursor):
    cursor.execute('''DROP TABLE IF EXISTS sites''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sites
                     (rank INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, HSTS BOOLEAN, max_age LONG, include_subdomains BOOLEAN, preload BOOLEAN, wrong_policy BOOLEAN)''')

def check_max_age(hs_array):
    if hs_array is None:
        return False
    elif hs_array[0] is not None and not re.fullmatch(max_age_regex, hs_array[0]):
        return True
    else:
        return False

def insert_site_data(cursor, url, hs_array):
    try:
        max_age_wrong = check_max_age(hs_array)
        cursor.execute("INSERT INTO sites (url, HSTS, max_age, include_subdomains, preload, wrong_policy) VALUES (?, ?, ?, ?, ?, ?)",
                       (url,
                        hs_array is not None,
                        int(hs_array[0].split("=")[1]) if hs_array is not None and not max_age_wrong else None,
                        include_subdomains_regex in hs_array if hs_array is not None else False,
                        preload_regex in hs_array if hs_array is not None else False,
                        max_age_wrong,))
    except Exception as e:
        print(f"Error inserting data for {url}: {e}")

def scrape_and_insert_data(cursor, latest_list, page):
    for domain in latest_list.top(100):
        url = "http://www." + domain if not domain.startswith("www.") else domain
        hs_array = fetch_hsts_policy(url, page)
        hs_array = [x.strip() for x in hs_array] if hs_array is not None else None
        insert_site_data(cursor, url, hs_array)

def get_data(cursor):
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_entries,
            SUM(CASE WHEN HSTS = 1 THEN 1 ELSE 0 END) AS hsts_true_entries,
            SUM(CASE WHEN include_subdomains = 1 THEN 1 ELSE 0 END) AS include_subdomains_true_entries,
            SUM(CASE WHEN preload = 1 THEN 1 ELSE 0 END) AS preload_true_entries,
            SUM(CASE WHEN wrong_policy = 1 THEN 1 ELSE 0 END) AS wrong_policy_true_entries
        FROM 
            sites
    """)

    results = cursor.fetchone()

    total_entries = results[0]
    hsts_true_entries = results[1]
    include_subdomains_true_entries = results[2]
    preload_true_entries = results[3]
    wrong_policy_true_entries = results[4]

    return total_entries, hsts_true_entries, include_subdomains_true_entries, preload_true_entries, wrong_policy_true_entries

def plot_pie_chart(labels, sizes, title):
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title(title)
    plt.savefig(title + ".png")

def analyze(cursor):
    total_entries, hsts_true_entries, include_subdomains_true_entries, preload_true_entries, wrong_policy_true_entries = get_data(cursor)

    hsts_labels = 'HSTS Inactive', 'HSTS Active'
    hsts_sizes = [total_entries - hsts_true_entries, hsts_true_entries]
    plot_pie_chart(hsts_labels, hsts_sizes, 'HSTS Status')

    pi_labels = 'Neither', 'Preload', 'Include Subdomains', 'Both', 'Wrong Policy'
    pi_sizes = [
        total_entries - (preload_true_entries + include_subdomains_true_entries),
        preload_true_entries,
        include_subdomains_true_entries,
        wrong_policy_true_entries,
        min(preload_true_entries, include_subdomains_true_entries, wrong_policy_true_entries)
    ]
    plot_pie_chart(pi_labels, pi_sizes, 'Preload or Include Subdomains')

def main():
    start = time.time()

    # Initialize Tranco
    t = Tranco(cache=True, cache_dir='.tranco')
    latest_list = t.list()

    # Connect to database
    conn = sqlite3.connect('tranco_sites.sqlite')
    c = conn.cursor()

    # Create database table
    create_database_table(c)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        
        # Scrape and insert data into database
        scrape_and_insert_data(c, latest_list, page)

    # Commit changes and close connection
    conn.commit()

    # Analyze the data and plot pie charts
    analyze(c)

    conn.close()

    end = time.time()
    print(f"Time elapsed: {end - start} seconds")

if __name__ == "__main__":
    main()
