import newspaper
import data_category
import blog_details_generate
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SUSL_Auto_Tech'))
import load_posts 
import csv
import time
import warnings

import requests
import re

import os
from datetime import datetime, timedelta
from dateutil import parser
from urllib.parse import urljoin
from newspaper import Article
from newspaper import Config

# Suppress the FutureWarning from newspaper source.py
warnings.simplefilter(action='ignore', category=FutureWarning)

config = Config()
config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
config.memoize_articles = False

cnn_paper = newspaper.build('https://www.cnn.com/business/tech', config=config, memoize_articles=True)
techcrunch_paper = newspaper.build('https://techcrunch.com/', config=config, memoize_articles=True)
wired_paper = newspaper.build('https://www.wired.com/', config=config, memoize_articles=True)
verge_news = newspaper.build('https://www.theverge.com/', config=config, memoize_articles=True)
cnet_news = newspaper.build('https://www.cnet.com/', config=config, memoize_articles=True)
techradar_news = newspaper.build('https://www.techradar.com/', config=config, memoize_articles=True)
techradar_news = newspaper.build('https://www.techradar.com/', config=config, memoize_articles=True)

def get_seen_urls(filename):
    seen = set()
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        seen.add(row[0]) # Assuming URL is first column
        except Exception as e:
            print(f"Error reading existing CSV {filename}: {e}")
    return seen

def is_recent(article_date):
    if article_date is None:
        return False
    cutoff = datetime.now() - timedelta(days=7)
    # Ensure article_date is offset-naive or offset-aware consistent with cutoff
    # easiest is to compare timestamps or make both naive
    if article_date.tzinfo:
         article_date = article_date.replace(tzinfo=None)
    return article_date >= cutoff

def collect_and_save(paper, filename):
    seen_urls = get_seen_urls(filename)
    print(f"Loaded {len(seen_urls)} existing articles from {filename}")

    for article in paper.articles:
        article_url = article.url
        # print(f"Processing: {article_url}")
        try:
            article.download()
            # If download fails, it might raise or just set html to None/empty, checking specific status codes isn't always easy directly on article object without accessing internal config or exception catching, 
            # but newspaper usually raises ArticleException on critical failures if configured, or we can check article.download_state
            
            article.parse()
            article.nlp()
            
            # Deduplication check
            if article_url in seen_urls:
                 print(f"Duplicate found, skipping: {article.title}")
                 continue

            # Date filtering
            # If publish_date is None, try to extract from URL if possible, or skip?
            # Start with simple check
            p_date = article.publish_date
            if not p_date:
                # Try to extract from URL if it matches /YYYY/MM/DD
                match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', article_url)
                if match:
                    try:
                        p_date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    except:
                        pass
            
            if not is_recent(p_date):
                print(f"Skipping old article ({p_date}): {article.title}")
                continue

            timestamp = time.time()
            
            # Save to CSV
            file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
            
            with open(filename, 'a', newline='', encoding='utf-8') as f:
               writer = csv.writer(f)
               #add headers only if file is new/empty
               if not file_exists:
                   writer.writerow(["article_url", "article_title", "article_summary", "publish_date", "article_authors", "timestamp","checked"])
               writer.writerow([article_url, article.title, article.summary, p_date, article.authors, timestamp,False])
               
            # Add to seen so we don't re-save in same run if duplicates exist
            seen_urls.add(article_url)
            
            print(f"Successfully collected: {article.title}")
            
            # Be polite to the server
            time.sleep(1) 
            
        except Exception as e:
            error_str = str(e)
            if "Status code 403" in error_str or "Status code 406" in error_str:
                print(f"Skipping {article_url}: Access Denied (Antibot protection)")
            else:
                print(f"Error processing {article_url}: {e}")

    print(f"Finished. Found {len(paper.articles)} articles in paper object.")

    # Fallback Mechanism
    if len(paper.articles) < 5:
        print("Scraper found few/no articles. Attempting manual fallback fetch...")
        try:
            base_url = paper.url
            # Re-use the user agent from config
            headers = {'User-Agent': config.browser_user_agent}
            response = requests.get(base_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Find links looking like articles (cnn.com/YYYY/MM/DD/...)
                # Regex matches href="..." where link contains /YYYY/MM/DD/
                # Captures absolute or relative starting with /
                # Used to be just date, now expanded for Wired (story/review)
                params = r'href=[\'"]((?:https?://[^"\']+)?/(?:story|review|article|\d{4}/\d{2}/\d{2})/[^"\']+)[\'"]'
                found_links = re.findall(params, response.text)
                
                # Deduplicate
                unique_links = set()
                for link in found_links:
                    link = urljoin(base_url, link)
                    unique_links.add(link)
                
                print(f"Fallback found {len(unique_links)} potential article links.")
                
                for link in unique_links:
                    try:
                        print(f"Fallback processing: {link}")
                        art = Article(link, config=config)
                        art.download()
                        art.parse()
                        art.nlp()
                        
                        # Deduplication in fallback
                        if link in seen_urls:
                            print(f"Falback Duplicate, skipping: {art.title}")
                            continue
                            
                        # Date filtering in fallback
                        p_date = art.publish_date
                        if not p_date:
                             match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
                             if match:
                                try:
                                    p_date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                                except:
                                    pass

                        if not is_recent(p_date):
                            print(f"Fallback Skipping old article ({p_date}): {art.title}")
                            continue

                        timestamp = time.time()
                        # Save to CSV
                        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
                        with open(filename, 'a', newline='', encoding='utf-8') as f:
                           writer = csv.writer(f)
                           if not file_exists:
                               writer.writerow(["article_url", "article_title", "article_summary", "publish_date", "article_authors", "timestamp", "checked"])
                           writer.writerow([link, art.title, art.summary, p_date, art.authors, timestamp, False])
                        
                        seen_urls.add(link)

                        print(f"Successfully collected: {art.title}")
                        time.sleep(1)
                    except Exception as e:
                         error_str = str(e)
                         if "Status code 403" in error_str or "Status code 406" in error_str:
                             pass # Silently skip in fallback to reduce noise
                         else:
                             print(f"Fallback Error on {link}: {e}")
            else:
                print(f"Fallback fetch failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Fallback mechanism failed: {e}")


collect_and_save(cnn_paper, 'collected_data/cnn.csv')
collect_and_save(techcrunch_paper, 'collected_data/techcrunch.csv')
collect_and_save(wired_paper, 'collected_data/wired.csv')
collect_and_save(verge_news, 'collected_data/verge_news.csv')
collect_and_save(cnet_news, 'collected_data/cnet_news.csv')
collect_and_save(techradar_news, 'collected_data/techradar_news.csv')

print("\nStarting data categorization...")
try:
    data_category.load_and_process_data()
    print("Data categorization complete.")
    blog_details_generate.save_to_file()
    print("Blog details generation complete.")
    load_posts.import_data()
    print("Data loading complete.")
except Exception as e:
    print(f"Error during categorization: {e}")
