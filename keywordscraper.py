#!/usr/bin/python3
#########################################################
#                                                       #
#           Website Keyword Scraper                     #
#           Created for fun by curtthecoder             #
#           February 26, 2025                           #
#                                                       #
#########################################################
import sys
import requests
from bs4 import BeautifulSoup
import argparse
import re
from urllib.parse import urlparse, urljoin
import html
import time
from concurrent.futures import ThreadPoolExecutor

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    UNDERLINE = "\033[4m"

def colorize(text, color):
    """Add color to text for terminal output."""
    return f"{color}{text}{Colors.RESET}"

def validate_url(url):
    """Validate if the provided string is a proper URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_base_url(url):
    """Extract base URL for resolving relative links."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def extract_links(soup, base_url):
    """Extract all links from the page."""
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Skip empty links, javascript, and anchors
        if not href or href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
            continue
        # Convert relative URLs to absolute
        full_url = urljoin(base_url, href)
        # Only include links from the same domain
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.append(full_url)
    return list(set(links))  # Remove duplicates

def scrape_page(url, keywords, case_sensitive=False, whole_word=False, depth=0, max_depth=1):
    """Scrape a single page for keywords and return results with URL context."""
    try:
        # Send request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Get both raw HTML and parsed text
        html_content = response.text
        
        # Parse content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Method 1: Standard text extraction
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Method 2: Get text from specific elements
        additional_text = ""
        for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'a', 'li', 'td']):
            if element.string:
                additional_text += " " + element.string
        
        # Method 3: Extract text from attributes
        attr_text = ""
        for element in soup.find_all(attrs={"title": True}):
            attr_text += " " + element["title"]
        for element in soup.find_all(attrs={"alt": True}):
            attr_text += " " + element["alt"]
        for element in soup.find_all('meta', attrs={"content": True}):
            attr_text += " " + element["content"]
        
        # Method 4: Extract text from JavaScript variables and data attributes
        js_text = ""
        for script in soup.find_all('script'):
            if script.string:
                js_text += " " + script.string
        for element in soup.find_all(True):
            for attr_name in element.attrs:
                if attr_name.startswith('data-'):
                    js_text += " " + str(element[attr_name])
        
        # Combine all text sources and decode HTML entities
        combined_text = html.unescape(text_content + " " + additional_text + " " + attr_text + " " + js_text)
        
        # Results for this page
        page_results = {"url": url, "matches": {}}
        
        # Search for keywords
        for keyword in keywords:
            # Prepare regex pattern based on options
            if whole_word:
                pattern_str = r'(.{0,40})\b(' + re.escape(keyword) + r')\b(.{0,40})'
            else:
                pattern_str = r'(.{0,40})(' + re.escape(keyword) + r')(.{0,40})'
                
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(pattern_str, flags)
            
            # Search in combined text
            matches = pattern.findall(combined_text)
            
            # Also search directly in HTML
            html_pattern = re.compile(re.escape(keyword), flags)
            html_matches = html_pattern.findall(html_content)
            total_matches = len(html_matches)
            
            if matches or total_matches > 0:
                page_results["matches"][keyword] = {
                    "count": total_matches,
                    "contexts": [(m[0], m[1], m[2]) for m in matches[:10]]  # Keep as tuples for colorization
                }
        
        # Get links for further crawling if needed
        links = []
        if depth < max_depth:
            base_url = get_base_url(url)
            links = extract_links(soup, base_url)
        
        return page_results, links
        
    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"Request error: {str(e)}"}, []
    except Exception as e:
        return {"url": url, "error": f"Processing error: {str(e)}"}, []

def scrape_website(start_url, keywords, case_sensitive=False, whole_word=False, max_depth=1, max_pages=20, colorize_output=True):
    """Scrape website and its pages for keywords."""
    try:
        # Add scheme if missing
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
            
        # Validate URL
        if not validate_url(start_url):
            return f"Invalid URL: {start_url}"
        
        # Track visited URLs to avoid duplicates
        visited = set()
        to_visit = [start_url]
        all_results = []
        
        # Process pages up to max_depth
        for depth in range(max_depth + 1):
            if not to_visit or len(visited) >= max_pages:
                break
                
            current_level = to_visit.copy()
            to_visit = []
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for url in current_level:
                    if url not in visited and len(visited) < max_pages:
                        visited.add(url)
                        futures.append(executor.submit(scrape_page, url, keywords, case_sensitive, whole_word, depth, max_depth))
                
                # Process results and collect new links
                for future in futures:
                    page_result, links = future.result()
                    all_results.append(page_result)
                    
                    # Add new links to visit in the next iteration
                    if depth < max_depth:
                        for link in links:
                 
                            if link not in visited and len(to_visit) + len(visited) < max_pages:
                                to_visit.append(link)
        
        # Format the results
        formatted_results = []
        keyword_summary = {k: {"total": 0, "pages": 0} for k in keywords}
        
        for page in all_results:
            if "error" in page:
                error_msg = f"\nError processing {page['url']}: {page['error']}"
                if colorize_output:
                    error_msg = colorize(error_msg, Colors.RED)
                formatted_results.append(error_msg)
                continue
                
            if not page.get("matches"):
                continue
                
            page_has_matches = False
            page_results = []
            
            # Add page URL with color
            if colorize_output:
                page_results.append(f"\n{colorize('Page:', Colors.BOLD)} {colorize(page['url'], Colors.BLUE + Colors.UNDERLINE)}")
            else:
                page_results.append(f"\nPage: {page['url']}")
            
            for keyword, data in page["matches"].items():
                if data["count"] > 0:
                    page_has_matches = True
                    keyword_summary[keyword]["total"] += data["count"]
                    keyword_summary[keyword]["pages"] += 1
                    
                    # Add keyword count with color
                    if colorize_output:
                        page_results.append(f"  {colorize('Keyword', Colors.BOLD)} '{colorize(keyword, Colors.GREEN)}': {colorize(str(data['count']), Colors.YELLOW)} occurrences")
                    else:
                        page_results.append(f"  Keyword '{keyword}': {data['count']} occurrences")
                    
                    if data["contexts"]:
                        page_results.append("  Contexts:")
                        for i, context_tuple in enumerate(data["contexts"], 1):
                            # Unpack the context parts
                            before, match, after = context_tuple
                            
                            # Clean up the context
                            before = re.sub(r'\s+', ' ', before).strip()
                            match = re.sub(r'\s+', ' ', match).strip()
                            after = re.sub(r'\s+', ' ', after).strip()
                            
                            # Format with color
                            if colorize_output:
                                colored_context = f"...{before}{colorize(match, Colors.RED + Colors.BOLD)}{after}..."
                                page_results.append(f"    {i}. {colored_context}")
                            else:
                                context = f"...{before}{match}{after}..."
                                page_results.append(f"    {i}. {context}")
                        
                        if data["count"] > len(data["contexts"]):
                            remaining = data["count"] - len(data["contexts"])
                            if colorize_output:
                                page_results.append(f"    ... and {colorize(str(remaining), Colors.YELLOW)} more occurrences")
                            else:
                                page_results.append(f"    ... and {remaining} more occurrences")
            
            if page_has_matches:
                formatted_results.append("\n".join(page_results))
        
        # Add summary at the beginning with colors
        summary = [colorize("Keyword Search Summary:", Colors.BOLD + Colors.MAGENTA) if colorize_output else "Keyword Search Summary:"]
        
        for keyword, data in keyword_summary.items():
            if data["total"] > 0:
                if colorize_output:
                    summary.append(f"- '{colorize(keyword, Colors.GREEN)}': Found {colorize(str(data['total']), Colors.YELLOW)} times across {colorize(str(data['pages']), Colors.CYAN)} pages")
                else:
                    summary.append(f"- '{keyword}': Found {data['total']} times across {data['pages']} pages")
            else:
                if colorize_output:
                    summary.append(f"- '{colorize(keyword, Colors.GREEN)}': {colorize('Not found', Colors.RED)} on any page")
                else:
                    summary.append(f"- '{keyword}': Not found on any page")
        
        scanned_msg = f"\nScanned {len(visited)} pages from {start_url}"
        if colorize_output:
            scanned_msg = f"\nScanned {colorize(str(len(visited)), Colors.CYAN)} pages from {colorize(start_url, Colors.BLUE)}"
        summary.append(scanned_msg)
        
        if not formatted_results:
            no_results_msg = "\nNo keywords found on any page."
            if colorize_output:
                no_results_msg = "\n" + colorize("No keywords found on any page.", Colors.RED)
            return "\n".join(summary) + no_results_msg
        
        return "\n".join(summary) + "\n" + "\n".join(formatted_results)
        
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        if colorize_output:
            error_msg = colorize(error_msg, Colors.RED)
        return error_msg

def main():
    parser = argparse.ArgumentParser(description='Scrape a website for specific keywords.')
    parser.add_argument('url', help='The URL of the website to scrape')
    parser.add_argument('keywords', nargs='+', help='Keywords to search for')
    parser.add_argument('-o', '--output', help='Output file to save results')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Enable case-sensitive matching')
    parser.add_argument('-w', '--whole-word', action='store_true', help='Match whole words only')
    parser.add_argument('-d', '--depth', type=int, default=1, help='Crawl depth (default: 1)')
    parser.add_argument('-p', '--max-pages', type=int, default=20, help='Maximum pages to scan (default: 20)')
    parser.add_argument('-n', '--no-color', action='store_true', help='Disable colorized output')
    
    args = parser.parse_args()
    
    # Determine if we should use colors (disable for file output)
    use_colors = not args.no_color and not args.output
    
    print(f"Scraping {args.url} for keywords: {', '.join(args.keywords)}")
    print(f"Options: depth={args.depth}, max_pages={args.max_pages}")
    
    results = scrape_website(
        args.url, 
        args.keywords, 
        args.case_sensitive, 
        args.whole_word,
        args.depth,
        args.max_pages,
        use_colors
    )
    
    if args.output:
        # Remove ANSI color codes for file output
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_results = ansi_escape.sub('', results)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(clean_results)
        print(f"Results saved to {args.output}")
    else:
        print(results)

if __name__ == "__main__":
    main()