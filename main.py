import csv
import requests
from bs4 import BeautifulSoup
from breachforums import extract_breachdata_breachforums_database, breachforums_cookies
from helpers import set_cookies, save_emails_to_csv, save_brandMentions_to_csv, extract_emails_from_directory
from opencti import save_emails_to_opencti, save_file_emails_to_opencti
from leakbase import extract_breachdata_leakbase_database 
from checkphish import checkphish_cookies,checkphish_headers, checkphish_url, extract_domain_impersonation_data 
from opencti import save_checkphish_to_opencti, save_emails_to_opencti, save_file_emails_to_opencti, save_brand_mentions_to_opencti,save_bins_to_opencti,save_labels_to_opencti
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv("requiredParameters.env")
    headers = {'User-Agent': 'PlaceHolder'}
    breachforums_session = requests.Session()
    set_cookies(breachforums_session, breachforums_cookies)
    breachforums_session.headers.update(headers)
    leakbase_session = requests.Session()
    domain = os.getenv("WATCHLIST_DOMAIN")
    subdomain = os.getenv("WATCHLIST_SUBDOMAIN")
    brandIndicators = os.getenv("WATCHLIST_BRAND_INDICATORS").split(',')
    binlist = os.getenv("WATCHLIST_BINLIST").split(',')
    emails_file = os.getenv("WATCHLIST_EMAILS_FILE")
    directory = "downloaded_breach_data" 
    """ Search for emails using domain and/or subdomain and/or emails file """
    #thread_emails_dict_breachforums = extract_breachdata_breachforums_database(breachforums_session, domain=domain, subdomain=subdomain, emails_file=emails_file)
    thread_emails_dict_leakbase = extract_breachdata_leakbase_database(leakbase_session, domain=domain, subdomain=subdomain, emails_file=emails_file)
    #thread_emails_dict_telegram = extract_emails_from_directory(directory, domain=domain, subdomain=subdomain, emails_file=emails_file)
    """ Save Emails to OpenCTI"""
    #save_emails_to_opencti(breachforums_session, thread_emails_dict_breachforums)
    #save_emails_to_opencti(leakbase_session, thread_emails_dict_leakbase)
    #save_file_emails_top_opencti(thread_emails_dict_telegram)
    """ Search for brand mentions in dark web """
    #b1 = extract_breachdata_breachforums_database(breachforums_session, brandIndicators=brandIndicators)
    #b2 = extract_breachdata_leakbase_database(leakbase_session, brandIndicators=brandIndicators)
    #b2.update(b1)
    """ Save Brand Mentions to OpenCTI"""
    #save_brand_mentions_to_opencti(leakbase_session, b2)
    """ Search for BINs in darkweb """
    #stolencard_dict_breachforums = extract_breachdata_breachforums_database(breachforums_session, binlist=binlist)
    #stolencard_dict_leakbase = extract_breachdata_leakbase_database(leakbase_session, binlist=binlist)
    """ Save BINs to OpenCTI"""
    #save_bins_to_opencti(breachforums_session,stolencard_dict_breachforums)
    #save_bins_to_opencti(leakbase_session, stolencard_dict_leakbase)
    """ Checking for suspicious lookalike Domains """
    #impersonation_data = extract_domain_impersonation_data(checkphish_cookies, checkphish_headers,checkphish_url)
    """ Saving suspicious lookalike domain data to OpenCTI """
    #save_labels_to_opencti(impersonation_data)   # Add domain scan categories as labels to opencti so we can filter scanned domains
    #save_checkphish_to_opencti(impersonation_data)     

""" Testing Spot """
#for file in telegram_emails_dict.keys():
    #    if telegram_emails_dict[file]:
    #        print(file, telegram_emails_dict[file])
    #
    #
#print(extract_last_page_number(session))

#response = session.get(base_url)
#links = extract_links(response.text, base_url)
#response = session.get("https://breachforums.st/Forum-Databases")
#links.extend(extract_links(response.text, base_url))
#for link in links:
#    print(link)
#with open("test.html","w") as f:
#    f.write(response.text)

#urls = []
