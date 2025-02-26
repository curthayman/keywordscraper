Website Keyword Scraper
A powerful Python tool for scraping websites to find specific keywords, showing their context, and identifying the pages where they appear.

Created for fun by curtthecoder

Features
🔍 Comprehensive Keyword Detection: Finds keywords in visible text, HTML attributes, meta tags, and even JavaScript
🌐 Website Crawling: Follows links to scan multiple pages within the same domain
🎯 Context Display: Shows the text surrounding each keyword match
🔗 URL Tracking: Identifies which pages contain your keywords
🎨 Colorized Output: Highlights keywords in search results for better visibility
📊 Summary Statistics: Provides an overview of keyword occurrences across the site
📁 File Export: Save results to a file for later analysis

**Installation**
Clone this repository:

**Clone this repository:**
```git clone https://github.com/curtthecoder/website-keyword-scraper.git```
```cd website-keyword-scraper```

**Install the required dependencies:**
```pip install -r requirements.txt```

**Basic usage:**
```python keyword_scraper.py example.com keyword1 keyword2 keyword3```

Command Line Options

python keyword_scraper.py [-h] [-o OUTPUT] [-c] [-w] [-d DEPTH] [-p MAX_PAGES] url keywords [keywords ...]

url: The website URL to scan

keywords: One or more keywords to search for

-o, --output: Save results to a file

-c, --case-sensitive: Enable case-sensitive matching

-w, --whole-word: Match whole words only

-d, --depth: Crawl depth (default: 1)

-p, --max-pages: Maximum pages to scan (default: 20)

Examples
Search for a single keyword:
```python keywordscraper.py example.com password```

Search for multiple keywords:
```python keywordscraper.py example.com username password email```

Search with a crawl depth of 2 (follows links to scan more pages):
```python keywordscraper.py example.com password -d 2```

Save results to a file:

```python keywordscraper.py example.com password -o results.txt```

Match whole words only (won't match "password" in "mypassword123"):

```python keywordscraper.py example.com password -w```

Output Example

Keyword Search Summary:
- 'password': Found 15 times across 3 pages
- 'username': Found 8 times across 2 pages
- 'email': Not found on any page

Scanned 5 pages from https://example.com

Page: https://example.com/login
  Keyword 'password': 7 occurrences
  Contexts:
    1. ...Enter your password to access your account...
    2. ...The password must be at least 8 characters...
    3. ...Forgot your password? Click here to reset...

Page: https://example.com/signup
  Keyword 'password': 5 occurrences
  Keyword 'username': 6 occurrences
  Contexts:
    1. ...Choose a username that is unique and memora...
    2. ...Your password should include numbers and sp...

Requirements
Python 3.6+
requests
beautifulsoup4
html5lib

License
This project is open source and available under the MIT License.

Disclaimer
This tool is for educational and legitimate testing purposes only. Always ensure you have permission to scan websites before using this tool.
