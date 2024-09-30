
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from helpers import scrape_from_page, extract_links, scrape_brand_from_page
import time

""" 
Terminology : 
    - Thread : User post that contains breach data
    - Database page : a page that contains multiple threads
"""

base_url = "https://breachforums.st/"

""" 
mybbuser : cookie necessary to validate login
__ddg1_ :  cookie necessary to bypass DDoS protection 
"""
load_dotenv("requiredParameters.env")
breachforums_user_cookie = os.getenv('BREACHFORUMS_USER_COOKIE')
breachforums_ddos_prevention_cookie = os.getenv('BREACHFORUMS_DDOS_PREVENTION_COOKIE')
#breachforum_cookies = {'mybbuser': '161506_AtJa9lyXqrNd0ZtoWix2joCRLFnzzVou0gEI6KmLxwr4VEIqZh', '__ddg1_': 'LbzckXRMXGAeIENq5lG1'}
breachforums_cookies = {'mybbuser': f"{breachforums_user_cookie}", '__ddg1_': f"{breachforums_ddos_prevention_cookie}"}
def extract_breachforums_last_page_number(session, url):
    """
        function that extracts last page number of forum (in order to later scrape all pages of forum for threads)
        input : - session : session object to use for requests
                - url : forum url
        output : last page number of forum
    """
    html = session.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    last_page = soup.find('a', class_='pagination_last')
    last_page_number = last_page.text.strip()
    return int(last_page_number)

def extract_breachforums_links(session, url):
    """
        function that extracts all database pages that contain threads
        input : - session : session object to use for requests
                - url : base url to extract threads from (any page will do)
        output : all links that contain threads in the forum
    """
    links = []
    last_page = extract_breachforums_last_page_number(session, url)
    for i in range(1, last_page + 1):
        params = {'page': i}
        url_with_params = f"{url}?{urlencode(params)}"
        links.append(url_with_params)
    return links

def extract_breachforums_live_database_pages(session):
    """ old refactored function """
    url = "https://breachforums.st/Forum-Databases"
    return extract_breachforums_links(session, url)

def extract_breachforums_removed_database_pages(session):
    """ old refactored function """
    url = "https://breachforums.st/Forum-Databases-Removed-Content"
    return extract_breachforums_links(session, url)


def extract_breachforums_thread_links(page, base_url):
    """ function that filters links and retrieves only thread links 
        input : - html : page content to look in
                - base_url : base url of website
        output : list of thread links embedded in the page   
    """
    urls = extract_links(page, base_url)
    filtered_urls = set()
    for url in urls:
        if url.startswith(base_url + "/Thread"):
            filtered_urls.add(url)
    return filtered_urls

def extract_breachforums_database_threads(session):
    """ function that retrieves a set of all thread links from breachforums
        input  : - session : session object to use for requests
        output : set of all thread links from breachforums
    """
    base_url = "https://breachforums.st"
    live_database_url = "https://breachforums.st/Forum-Databases"
    removed_database_url = "https://breachforums.st/Forum-Databases-Removed-Content"
    live_database_links = extract_breachforums_links(session, live_database_url)
    removed_database_links = extract_breachforums_links(session, removed_database_url)
    database_links = live_database_links + removed_database_links
    threads = set()
    for database_link in database_links:
        print("Extracting Threads from page", database_link)
        response = session.get(database_link)
        while (response.status_code != 200):
            print("Error Response from database link:", database_link)
            time.sleep(3)
            response = session.get(database_link)
            print("Extracting Threads from page", database_link)
        page = response.text
        page_threads = extract_breachforums_thread_links(page, base_url)
        threads.update(page_threads)
    return threads

def extract_breachdata_breachforums_database(session, domain=None, emails_file=None, brandIndicators=None, subdomain=None, binlist=None):
    """ function that retrieves all breached emails / brand mentions from breachforums, this function is 
        the main entry point, it uses all helper and breachforum functions
        input : - session : session object to use for requests
                - domain : domain that we want to look for breached accounts in (optional) 
                - emails_file : file of customer emails that we want to detect breaches in (optional)
                - brandIndicators : list of brand indicators to look for (optional)
                - subdomain : subdomain that we want to look for breached accounts in (optional)
        output : all breach data found in breachforums (emails, brand mentions) depending on inputs given
    """
    thread_emails_dict = dict()
    brand_mentions_dict = dict()
    stolencards_dict = dict()
    threads = extract_breachforums_database_threads(session)
    #threads = ["https://breachforums.st/Thread-random-breaches", "https://breachforums.st/Thread-2024-Latest-Indonesia-credit-card-Post-Bank-User-1M-Data-Leakk"]
    currentThread = 1
    totalNumberThreads = len(threads)
    current_time_spent = 0
    max_retries = 3
    start_time = time.time()
    for thread in threads:
        currentThread += 1
        retries = 0
        retryTime = 1
        while retries < max_retries : 
            request_start_time = time.time()
            estimated_time = ((current_time_spent) / currentThread) * totalNumberThreads - current_time_spent 
            try:                
                print("Extracting breach data from thread", thread, f"{(currentThread / totalNumberThreads) * 100:.2f}", f"{estimated_time:.2f}")
                response = session.get(thread)
                if response.status_code == 200:
                    html = response.text
                    break
                else:
                    print(f"Error Response from thread {thread}, Status Code: {response.status_code}")
            except Exception as e:
                print(f"Connection to {thread} failed with error {e}")
            retries += 1
            if retries < max_retries:
                print("Retrying in:", retryTime)
                time.sleep(retryTime)
                retryTime *= 2
            else:
                print(f"Max retries for thread", thread)
        request_end_time = time.time()
        current_time_spent = request_end_time - start_time
        if domain is not None or emails_file is not None or subdomain is not None:
            thread_emails = scrape_from_page(html, domain=domain, emails_file=emails_file, subdomain=subdomain)
            if thread_emails:
                print("Found emails", thread_emails, "in thread", thread)
            thread_emails_dict[thread] = thread_emails
        if brandIndicators is not None:
            brandMentions = scrape_from_page(html, brandIndicators=brandIndicators)
            if brandMentions:
                print("Found brand mentions", brandMentions, "in thread", thread)
            brand_mentions_dict[thread] = brandMentions
        if binlist is not None:
            stolencards = scrape_from_page(html, binlist=binlist)
            if stolencards:
                print("Found stolen cards : ", stolencards, "in thread", thread)
            stolencards_dict[thread] = stolencards
    if brandIndicators is not None and (domain is not None or emails_file is not None or subdomain is not None):
        return thread_emails_dict, brand_mentions_dict
    elif brandIndicators is not None:
        with open("breachforums_scrape_metadata.txt","w") as file:
            file.write(f"Number of scraped pages : {len(brand_mentions_dict)}")
        return brand_mentions_dict
    elif domain is not None or emails_file is not None or subdomain is not None:
        with open("breachforums_scrape_metadata.txt", "w") as file:
            file.write(f"Number of scraped pages : {len(thread_emails_dict)}")
        return thread_emails_dict
    elif binlist is not None:
        with open("breachforums_scrape_metadata.txt", "w") as file:
            file.write(f"Numebr of scraped pages : {len(stolencards_dict)}")
        return stolencards_dict



