import requests
from bs4 import BeautifulSoup
from helpers import extract_links, scrape_from_page, scrape_brand_from_page
import time

def extract_leakbase_last_page_number(session, url):
    """
        function that extracts last page number of forum (in order to later scrape all pages of forum for threads)
        input : - session : session object to use for requests
                - url : forum url
        output : last page number of forum
    """
    html = session.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    result = soup.find(lambda tag: tag.name == 'li' and tag.get('class') == ['pageNav-page'])
    last_page_number = result.text.strip()
    return int(last_page_number)

def extract_leakbase_links(session, url):
    """
        function that extracts all database pages that contain threads
        input : - session : session object to use for requests
                - url : base url to extract threads from (any page will do)
        output : all links that contain threads in the forum
    """
    links = []
    last_page = extract_leakbase_last_page_number(session, url)
    for i in range(1, last_page + 1):
        page_endpoint = f"page-{i}"
        url_with_params = f"{url}{page_endpoint}"
        links.append(url_with_params)
    return links

def extract_leakbase_thread_links(page, base_url):
    """ function that filters links and retrieves only thread links 
        input : - html : page content to look in
                - base_url : base url of website
        output : list of thread links embedded in the page   
    """
    urls = extract_links(page, base_url)
    filtered_urls = set()
    for url in urls:
        if url.startswith(base_url + "/threads/"):
            filtered_urls.add(url)
    return filtered_urls

def extract_leakbase_database_threads(session):
    """ function that retrieves a set of all thread links from leakbase
        input  : - session : session object to use for requests
        output : set of all thread links from leakbase
    """
    base_url = "https://leakbase.io"
    big_leaks_database_url = "https://leakbase.io/forums/big/"
    big_leaks_database_links = extract_leakbase_links(session, big_leaks_database_url)
    database_links = big_leaks_database_links
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
        page_threads = extract_leakbase_thread_links(page, base_url)
        threads.update(page_threads)
    return threads

def extract_breachdata_leakbase_database(session, domain=None, emails_file=None, brandIndicators=None, subdomain=None, binlist=None):
    """ function that retrieves all breached emails / brand mentions from leakbase, this function is 
        the main entry point, it uses all helper and breachforum functions
        input : - session : session object to use for requests
                - domain : domain that we want to look for breached accounts in (optional) 
                - emails_file : file of customer emails that we want to detect breaches in (optional)
                - brandIndicators : list of brand indicators to look for (optional)
                - subdomain : subdomain that we want to look for breached accounts in (optional)
        output : all breach data found in leakbase (emails, brand mentions) depending on inputs given
    """
    thread_emails_dict = dict()
    brand_mentions_dict = dict()
    stolencards_dict = dict()
    threads = extract_leakbase_database_threads(session)
    #threads = ["https://leakbase.io/threads/bingehacker-brand.27883/","https://leakbase.io/threads/indonesias-civil-administration-data-breach.25768/"]
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
        if domain is not None or subdomain is not None or emails_file is not None:
            thread_emails = scrape_from_page(html, domain=domain, subdomain=subdomain,emails_file=emails_file)
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
                print("Found stolen cards", stolencards, "in thread", thread)
            stolencards_dict[thread] = stolencards
    if brandIndicators is not None and (domain is not None or subdomain is not None or emails_file is not None):
        return thread_emails_dict, brand_mentions_dict
    elif brandIndicators is not None:
        with open("leakbase_scrape_metadata.txt", "w") as file:
            file.write(f"Number of scraped pages : {len(brand_mentions_dict)}")
        return brand_mentions_dict
    elif domain is not None or subdomain is not None or emails_file is not None:
        with open("leakbase_scrape_metadata.txt", "w") as file:
            file.write(f"Number of scraped pages : {len(thread_emails_dict)}")
        return thread_emails_dict
    elif binlist is not None:
        with open("leakbase_scrape_metada.txt", "w") as file:
            file.write(f"Number of scraped pages : {len(thread_emails_dict)}")
        return stolencards_dict
