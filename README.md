# HSTS-Web-Crawler
This web crawler aims to measure the state of **HSTS policy adoption** on the Web.

## HSTS (HTTP Strict Transfer Protocol)
**HSTS** is a web security mechanism that helps protect users against **man-in-the-middle attacks** and other **data security threats** while browsing the Internet. **HSTS** is an **HTTP header** that web servers can send to browsers to indicate that they should always communicate with the site via **HTTPS** instead of **HTTP**, even if the user attempts to access the site via **HTTP**.

**HSTS** can include various options to customize its behavior:
1. **max-age**: specifies how long the browser should remember the **HSTS policy** for a site, expressed in seconds.
2. **includeSubDomains**: if True, the **HSTS policy** will also be applied to all subdomains of the main site; otherwise, only to the main domain.
3. **preload**: if a site is included in a browser's **preload list**, the browser will store the **HSTS policy** for that site even before visiting it for the first time.

## Web crawler implementation
The web crawler was implemented using the **Playwright** Python library to automate interaction with the browser. The choice was driven by its flexibility and ability to support different browsers.
**Playwright** is a framework that allows developing **browser-level web crawlers**, which automate interaction with the browser, enabling actions such as clicking on links, submitting forms, and collecting dynamically generated data from JavaScript.
This type of web crawler was chosen over other options, such as **application-level crawlers** implemented by libraries like requests or **user-level crawlers** implemented by libraries like Puppeteer, due to its lower detection rate. This makes it possible to obtain information from sites that would have detected and blocked attempts to collect data by other types of web crawlers. **Browser-level web crawlers**, like those implemented by **Playwright**, are indeed less detectable by sites, offering significant advantages in terms of flexibility and robustness.

## Selected websites
To conduct a thorough analysis, the **top 1000 sites** in the **Tranco list**, a widely used data source in web security research, were selected.
Only the **top 1000 sites** were considered, as the choice of web crawler involved a trade-off between the number of sites from which data collection would be successful and the time required to perform such collection.

## Plots generation
At the end of the crawling procedure, all the statistics are analyzed and the results are clearly visible in the plots you can find in the **img folder**.

### Contributors
- **Elisa Rizzo**
- **Pietro Visconti**
