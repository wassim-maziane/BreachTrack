from pycti import OpenCTIApiClient
import requests
from urllib.parse import urlparse
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
opencti_url = os.getenv("OPENCTI_URL")
api_token = os.getenv("OPENCTI_API_TOKEN")
#opencti_url = "http://192.168.254.130:8080"
#api_token = "17d4bf5c-7e6f-4117-b43c-87183aad84c2"

def save_labels_to_opencti(json_data):
    client = OpenCTIApiClient(opencti_url, api_token)
    shades_of_red = [
    "#F08080",  # Light Coral
    "#FA8072",  # Salmon
    "#CD5C5C",  # Indian Red
    "#DC143C",  # Crimson
    "#B22222",  # Firebrick
    "#8B0000",  # Dark Red
    "#800000"   # Maroon
]
    labels = set()
    domain = "cihbank.ma"
    domainResults = json_data["scanResults"][domain] 
    typosquattingresults = domainResults["typosquattingResult"]["result"]
    for domainScan in typosquattingresults:
        if "final_category" in domainScan:
            labels.add(domainScan["final_category"])
    i = 0
    for category in labels:
        label = client.label.create(value=category, color=shades_of_red[i])
        i += 1

def save_checkphish_to_opencti(json_data):
    client = OpenCTIApiClient(opencti_url, api_token)
    domain = "cihbank.ma"
    domainResults = json_data["scanResults"][domain]
    scannedVariantsCount = domainResults["metadata"]["totalVariants"]
    resolvedVariantsCount = domainResults["metadata"]["totalResolvedVariants"]
    typosquattingresults = domainResults["typosquattingResult"]["result"]
    for index,domainScan in enumerate(typosquattingresults):
        print(index)
        lookalike_domain = domainScan["domain"]
        lookalike_url = domainScan["src_url"]
        lookalike_ip_list = domainScan["ipv4"]
        mx_record_list = domainScan["mx"]
        risk_score = domainScan["risk_score"] * 20
        nameserversList = domainScan["ns"]
        scan_timestamp = domainScan["scan_ts"]
        timestamp = datetime.utcfromtimestamp(int(scan_timestamp) / 1000)
        takedown_enquiry = domainScan["takedown_enquiry"]
        if "has_mx_records" in domainScan:
            has_mx_records = domainScan["has_mx_records"]
            imagePath = domainScan["imagePath"]
            final_category = domainScan["final_category"]
            disposition = domainScan["disposition"]
            as_description = domainScan["as_description"]
        domain_description = f"Autonomous System : {as_description} ; \nLast Scan Timestamp : {timestamp}"
        domain_observable = client.stix_cyber_observable.create(simple_observable_key="Domain-Name.value", simple_observable_value=lookalike_domain, \
        simple_observable_description=domain_description, x_opencti_score=risk_score, objectLabel=final_category)
        lookalike_url_observable = client.stix_cyber_observable.create(simple_observable_key="Url.value", simple_observable_value=lookalike_url, \
        x_opencti_score=risk_score, objectLabel="URL Lookalike")
        url_relationship = client.stix_core_relationship.create(fromId=domain_observable["id"], toId=lookalike_url_observable["id"], relationship_type="related-to")
        if lookalike_ip_list:
            for lookalike_ip in lookalike_ip_list:
                lookalike_ip_observable = client.stix_cyber_observable.create(simple_observable_key="IPv4-Addr.value", simple_observable_value=lookalike_ip \
                ,x_opencti_score=risk_score)
                ip_relationship = client.stix_core_relationship.create(fromId=domain_observable["id"],toId=lookalike_ip_observable["id"], relationship_type="resolves-to")
        if nameserversList:
            for nameserver in nameserversList[0].split("; "):
                if nameserver[-1] == ".":
                    nameserver = nameserver[:-1]
                nameserver_observable = client.stix_cyber_observable.create(simple_observable_key="Domain-Name.value", simple_observable_value=nameserver, objectLabel="nameserver")
                nameserver_relationship = client.stix_core_relationship.create(fromId=nameserver_observable["id"],toId=domain_observable["id"],relationship_type="related-to")
        if "registrar" in domainScan:
            registrar = domainScan["registrar"]
            registrar_observable = client.stix_cyber_observable.create(simple_observable_key="text.value", simple_observable_value=f"Registrar : {registrar}")
            registrar_relationship = client.stix_core_relationship.create(fromId=registrar_observable["id"],toId=domain_observable["id"], relationship_type="related-to", objectLabel="Registrar")
        if "has_mx_records" in domainScan:
            if has_mx_records:
                client.stix_cyber_observable.add_label(id=domain_observable["id"],label_name="mail lookalike")
            client.stix_cyber_observable.add_label(id=domain_observable["id"], label_name=disposition)
            if mx_record_list:
                for mx_record in mx_record_list:
                    if mx_record[-1] == ".":
                        mx_record = mx_record[:-1]
                    if mx_record:
                        if mx_record != lookalike_domain:
                            mx_record_observable = client.stix_cyber_observable.create(simple_observable_key="Domain-Name.value", simple_observable_value=mx_record \
                            ,x_opencti_score=risk_score, objectLabel="MX Record")
                            mx_relationship = client.stix_core_relationship.create(fromId=domain_observable["id"],toId=mx_record_observable["id"], relationship_type="resolves-to")
                        else:
                            client.stix_cyber_observable.add_label(id=domain_observable["id"], label_name="MX Record")
            imageResponse = requests.get(imagePath)
            artifact = client.stix_cyber_observable.upload_artifact(file_name=f"{lookalike_domain}.png", data=imageResponse.content, mime_type="image/png" \
                , x_opencti_description="Snapshot at time of scan", objectLabel="snapshot")
            artifact_relatonship = client.stix_core_relationship.create(fromId=artifact["id"], toId=domain_observable["id"], relationship_type="related-to")
        with open("checkphish_api_call_metadata.txt", "w") as file:
            file.write(f"Scanned Variants Count : {scannedVariantsCount}\nRegistered Variants Count : {resolvedVariantsCount}")

""" this function is for when we are extracting from the web (the dictionnary has urls for keys)  """
def save_emails_to_opencti(session, emails_dict):
    client = OpenCTIApiClient(opencti_url, api_token)
    for url in emails_dict:
        if emails_dict[url]:
            response = session.get(url)
            parsed_url = urlparse(url)
            filename = parsed_url.path.lstrip('/')
            artifact_description = f"Page found in : {url}"
            artifact = client.stix_cyber_observable.upload_artifact(file_name=filename, data=response.text, mime_type="text/html", x_opencti_description=artifact_description, objectLabel="dark web breach")
            url_observable = client.stix_cyber_observable.create(simple_observable_key="Url.value", simple_observable_value=url)
            for email in emails_dict[url]:
                email_description = f"Email found in {url}"
                email_observable = client.stix_cyber_observable.create(simple_observable_key="Email-Addr.value", simple_observable_value=email, simple_observable_description=email_description,objectLabel="dark web breach")
                relationship_description = "Breached Email found in Dark Web Thread"
                artifact_email_relationship = client.stix_core_relationship.create(fromId=email_observable["id"],toId=artifact["id"], relationship_type="related-to", description=relationship_description)
                url_email_relationship = client.stix_core_relationship.create(fromId=email_observable["id"],toId=url_observable["id"], relationship_type="related-to", description=relationship_description)
                #client.stix_cyber_observable.remove_label(id=email_observable["id"],label_name="data breach")
                #client.stix_cyber_observable.remove_label(id=artifact["id"],label_name="data breach")

""" this function is for when we are extracting from files (file sources currently : telegram channels)"""
def save_file_emails_to_opencti(emails_dict):
    client = OpenCTIApiClient(opencti_url, api_token)
    for filepath in emails_dict:
        if emails_dict[filepath]:
            file = open(filepath, "r")
            filedata = file.read()
            filename = os.path.basename(os.path.normpath(filepath))
            artifact = client.stix_cyber_observable.upload_artifact(file_name=filename, data=filedata, mime_type="text/plain", x_opencti_description=filepath.split('/')[1], objectLabel="telegram breach")
            email_description = f"Breached email found in telegram channel : {filepath.split('/')[1]}"
            for email in emails_dict[filepath]:
                email_observable = client.stix_cyber_observable.create(simple_observable_key="Email-Addr.value", simple_observable_value=email, simple_observable_description=email_description,objectLabel="telegram breach")
                relationship_description = f"This Email was found in telegram channel : {filepath.split('/')[1]}"
                relationship = client.stix_core_relationship.create(fromId=email_observable["id"],toId=artifact["id"], relationship_type="related-to", description=relationship_description)
                #client.stix_cyber_observable.remove_label(id=email_observable["id"],label_name="data breach")
                #client.stix_cyber_observable.remove_label(id=artifact["id"],label_name="data breach")

def save_brand_mentions_to_opencti(session, brand_dict):
    client = OpenCTIApiClient(opencti_url, api_token)
    for url in brand_dict:
        if brand_dict[url]:
            response = session.get(url)
            print(response.text)
            parsed_url = urlparse(url)
            filename = parsed_url.path.lstrip('/')
            artifact_description = f"Snapshot of page : {url}"
            artifact = client.stix_cyber_observable.upload_artifact(file_name=filename, data=response.text, mime_type="text/html", x_opencti_description=artifact_description, objectLabel="brand mention")
            url_observable = client.stix_cyber_observable.create(simple_observable_key="Url.value", simple_observable_value=url)
            mention_description = f"Brand Mention found in {url}"
            relationship_description = "Brand mention found in Dark Web Thread"
            for brandMention in brand_dict[url]:
                mention_observable = client.stix_cyber_observable.create(simple_observable_key="text.value", simple_observable_value=brandMention, simple_observable_description=mention_description,objectLabel="brand mention")
                mention_url_relationship = client.stix_core_relationship.create(fromId=mention_observable["id"], toId=artifact["id"], relationship_type="related-to")
                mention_artifact_relationship = client.stix_core_relationship.create(fromId=mention_observable["id"],toId=artifact["id"], relationship_type="related-to", description=relationship_description)
                    #client.stix_cyber_observable.remove_label(id=email_observable["id"],label_name="data breach")
                    #client.stix_cyber_observable.remove_label(id=artifact["id"],label_name="data breach")

def save_bins_to_opencti(session, stolencards_dict):
    client = OpenCTIApiClient(opencti_url, api_token)
    for url in stolencards_dict:
        if stolencards_dict[url]:
            response = session.get(url)
            parsed_url = urlparse(url)
            filename = parsed_url.path.lstrip('/')
            artifact_description = f"Snapshot of page {url}"
            artifact = client.stix_cyber_observable.upload_artifact(file_name=url, data=response.text, mime_type="text/html", x_opencti_description=artifact_description, objectLabel="stolen card")
            url_observable = client.stix_cyber_observable.create(simple_observable_key="Url.value", simple_observable_value=url)
            for stolencard in stolencards_dict[url]:
                card_description = f"Card compromised in {url}"
                card_observable = client.stix_cyber_observable.create(simple_observable_key="payment-card.card_number", simple_observable_value=stolencard, \
                                    simple_observable_description=card_description, objectLabel="stolen card")
                card_url_relationship = client.stix_core_relationship.create(fromId=card_observable["id"], toId=url_observable["id"], relationship_type="related-to")
                card_artifact_relationship = client.stix_core_relationship.create(fromId=card_observable["id"], toId=artifact["id"], relationship_type="related-to")
