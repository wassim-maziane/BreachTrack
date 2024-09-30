from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import csv
import os

def save_emails_to_csv(results_dict, filename):
    """ functions that saves breached email scraper results to csv
        input : - results_dict : dictionnary of thread (keys) - breached emails (values)
                - filename : name of file to write to
        output : writes results to a csv file with two columns : threads, compromised emails
    """
    with open(filename, mode='w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(['Threads', 'Compromised Emails'])
        for thread, emails in results_dict.items():
            if emails:
                for email in emails:
                    writer.writerow([thread, email])
    with open("last_scrape_metadata.txt", mode='w') as file:
        file.write(f"Number of threads scraped of last execution: {len(results_dict)}")

def save_brandMentions_to_csv(results_dict, filename):
    """ function that saves brand mentions scraper results to csv
        input : - results_dict : dictionnary of thread (keys) - brand mentions (values)
                - filename : name of file to write to
        output : writes results dictionnary to a csv file with two columns : threads(keys), brand mentions(values)
    """
    with open(filename, mode='w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(['Threads', 'Brand Mentions'])
        for thread, brandMentions in results_dict.items():
            if brandMentions:
                for brandMention in brandMentions:
                    writer.writerow([thread, brandMention])
    with open("last_scrape_metadata.txt", mode='w') as file:
        file.write(f"Number of threads scraped of last execution: {len(results_dict)}")
   
def save_to_html(html, filename):
    """ test function, writes html data to a file
        input : - html : html page content 
                - filename : name of file to write to
        output : writes html to a file
    """
    with open(filename, mode='w') as file:
        file.write(html)

def extract_emails_from_directory(directory, domain=None, emails_file=None, subdomain=None): 
    if not os.path.isdir(directory):
        print(f"{directory} doesn't exist")
        return
    email_results = dict()
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            breached_emails = scrape_emails_from_file(file_path, domain=domain, emails_file=emails_file, subdomain=subdomain)
            email_results[file_path] = breached_emails
    return email_results

def scrape_brand_from_page(html, brandIndicators):
    """
        function that searches for brand mentions in a page
        input : - html : html page content to look in
                - brandIndicators : list of brand indicators to look for
        output : list of brand mentions

    """
    page = BeautifulSoup(html, 'html.parser')
    page_text = page.get_text().lower()
    brandMentions = []
    for brandIndicator in brandIndicators:
        if brandIndicator in page_text:
            brandMentions.append(brandIndicator)
    return brandMentions


def scrape_emails_from_file(filename, domain=None, emails_file=None, subdomain=None, brandIndicators=None):
    """
        function that searches for breached emails in a page, we can either specify a domain, a file of customer emails or both
        input : - html : html page content to look in
                - domain : domain that we want to look for breached accounts in 
                - emails_file : file of customer emails that we want to detect breaches in
        output : set of breached emails found in page
    """
    file = open(filename, "r")
    file_data = file.read().lower()
    found_emails = []
    if brandIndicators is not None:
        brandMentions = []
        for brandIndicator in brandIndicators:
            if brandIndicator in file_data:
                brandMentions.append(brandIndicator)
        return set(brandMentions)
    if subdomain is not None:
        subdomain_escaped = re.escape(subdomain)
        pattern = rf"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.{subdomain_escaped}\b"
        emails = re.findall(pattern, file_data)
        found_emails.extend(emails)
            # Any domain except for gmail        pattern = r'\b[A-Za-z0-9._%+-]+@(?!gmail\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    if domain is not None:
        domain_escaped = re.escape(domain)
        pattern = rf'\b[A-Za-z0-9._%+-]+@{domain_escaped}\b'
        emails = re.findall(pattern, file_data)
        found_emails.extend(emails)
    if emails_file is not None:
        with open(emails_file) as file:
            for line in file:
                searched_email = line.strip()
                if searched_email in file_data:
                    found_emails.append(searched_email)
    return set(found_emails)


def scrape_from_page(html, domain=None, emails_file=None,subdomain=None, brandIndicators=None, binlist=None):
    """
        function that searches for breached emails in a page, we can either specify a domain, a file of customer emails or both
        input : - html : html page content to look in
                - domain : domain that we want to look for breached accounts in 
                - emails_file : file of customer emails that we want to detect breaches in
        output : set of breached emails found in page
    """
    page = BeautifulSoup(html, 'html.parser')
    page_text = page.get_text().lower()
    found_emails = []
    if domain == True:
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.ma\b"
        emails = re.findall(pattern, page_text)
        found_emails.extend(emails)
        return found_emails
        # Any domain except for gmail        pattern = r'\b[A-Za-z0-9._%+-]+@(?!gmail\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    elif binlist is not None:
        allstolencards = []
        for identifier in binlist:
            pattern = rf'\b\w*{identifier}\w*\b'
            stolencards = re.findall(pattern, page_text)
            allstolencards.extend(stolencards)
        return set(allstolencards)
    elif brandIndicators is not None:
        brandMentions = []
        for brandIndicator in brandIndicators:
            if brandIndicator in page_text:
                brandMentions.append(brandIndicator)
        return set(brandMentions)
    if subdomain is not None:
        subdomain_escaped = re.escape(subdomain)
        pattern = rf"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.{subdomain_escaped}\b"
        emails = re.findall(pattern, page_text)
        found_emails.extend(emails)
    if domain is not None:
        domain_escaped = re.escape(domain)
        pattern = rf'\b[A-Za-z0-9._%+-]+@{domain_escaped}\b'
        emails = re.findall(pattern, page_text)
        found_emails.extend(emails)
    if emails_file is not None:
        with open(emails_file) as file:
            for line in file:
                searched_email = line.strip()
                if searched_email in page_text:
                    found_emails.append(searched_email)
    return set(found_emails)

def extract_links(html, base_url):
    """
        function that searches for all embedded links in a page
        input : - html : page content to look in
                - base_url : base url of website
        output : list of links embedded in the page
    """
    page = BeautifulSoup(html, 'html.parser')
    hrefs = set([urljoin(base_url, a['href']).split('?')[0] for a in page.find_all('a', href=True)])
    return hrefs

def set_cookies(session, cookies):
    """
        function that sets cookies of a session object
        input : - session : session object to manipulate
                - cookies : dictionnary of cookies to set
        output : sets cookies for input session object
    """
    for key in cookies.keys():
        session.cookies.set(key, cookies[key])

def set_cookies_headers(session, cookies, headers):
    for key in cookies.keys():
        session.cookies.set(key, cookies[key])
    session.headers.update(headers)

def scrape_brand_from_page(html, brandIndicators):
    """
        function that searches for brand mentions in a page
        input : - html : html page content to look in
                - brandIndicators : list of brand indicators to look for
        output : list of brand mentions

    """
    page = BeautifulSoup(html, 'html.parser')
    page_text = page.get_text().lower()
    brandMentions = []
    for brandIndicator in brandIndicators:
        if brandIndicator in page_text:
            brandMentions.append(brandIndicator)
    return brandMentions

def scrape_emails_from_website(start_url, session):
    """
        test function : abandonned method of scraping email accounts
    """
    to_visit = start_url
    visited = set()
    emails = []
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        response = session.get(current_url)
        time.sleep(2)
        emails.extend(scrape_emails_from_page(response.text))
        visited.add(current_url)
        hrefs = extract_links(response.text)


