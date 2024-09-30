import requests
from helpers import set_cookies_headers
import json
import os
from dotenv import load_dotenv

load_dotenv()
checkphish_user_cookie = os.getenv("CHECKPHISH_USER_COOKIE")
checkphish_cookies = {"tau": checkphish_user_cookie}
#checkphish_cookies = {"tau": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDk1MjAsImV4cCI6MTcyMzYzOTk3NTI0NSwiaWF0IjoxNzIyNDMwMzc1fQ.5iSPb72ur2xjSAH6DYw4BJciGHsOS-o9U2UJAYrBlkw"}
checkphish_headers = {'content-type': 'application/json'}
checkphish_url = "https://app.checkphish.ai/platform-api/v1/typosquatting/search" 

def extract_domain_impersonation_data(cookies, headers, url):
    session = requests.Session()
    set_cookies_headers(session, cookies, checkphish_headers)
    body = {"searchType":"all"}
    response = session.post(url, json=body)
    data = response.json()
    with open('response.json', 'w') as file:
        json.dump(data, file, indent=4)      # duming the file in local folder to analyze checkphish api output
    return data
    # domain = "cihbank.ma"
    # domainResults = data["scanResults"][domain]
    # scannedVariantsCount = domainResults["metadata"]["totalVariants"]
    # resolvedVariantsCount = domainResults["metadata"]["totalResolvedVariants"]
    # typosquattingresults = domainResults["typosquattingResult"]["result"]
    # for index,domainScan in enumerate(typosquattingresults):
    #     lookalike_domain = domainScan["domain"]
    #     lookalike_url = domainScan["src_url"]
    #     lookalike_ip_list = domainScan["ipv4"]
    #     mx_record_list = domainScan["mx"]
    #     risk_score = domainScan["risk_score"]
    #     nameserversList = domainScan["ns"]
    #     scan_timestamp = domainScan["scan_ts"]
    #     takedown_enquiry = domainScan["takedown_enquiry"]
    #     if "has_mx_records" in domainScan:
    #         has_mx_record = domainScan["has_mx_records"]
    #         imagePath = domainScan["imagePath"]
    #         registrar = domainScan["registrar"]
    #         final_category = domainScan["final_category"]
    #         disposition = domainScan["disposition"]
    #         as_description = domainscan["as_description"]


    

