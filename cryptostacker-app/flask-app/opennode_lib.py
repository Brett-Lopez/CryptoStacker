import requests
from requests.api import head, request
import CSR_service_mesh_map
import CSR_toolkit
import json
import datetime
import urllib.parse
import logging

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

#https://developers.opennode.com/docs
base_url = CSR_service_mesh_map.opennode_api_base_url

def generate_headers(api_key):
    logging.critical("generate_headers() called")
    headers = {"Authorization": str(api_key)}
    return headers

def create_charge(api_key, fiat_amount, fiat_denomination, customer_email_address, description):
    logging.critical("create_charge() called")
    headers = generate_headers(api_key)
    headers["Content-Type"] = "application/json"
    payload = {
        "description": description, #which tier are they signing up for and how many months?
        "amount": fiat_amount,
        "currency": fiat_denomination,
        "customer_email": customer_email_address,
        "notif_email": customer_email_address,
        "success_url": "https://www.cryptostacker.io/subscribe/manage_subscription",
        "auto_settle": False,
        "ttl": 1440
    }
    endpoint_url = "/v1/charges"
    query_url = base_url + endpoint_url
    logging.error(query_url)
    requests_response = requests.post(query_url, data=json.dumps(payload), headers=headers)
    if requests_response.status_code == 200:
        logging.error(requests_response.json()) #debugging
        return requests_response.json()
    else:
        logging.error(requests_response.json()) #debugging
        return {"failed": "failed"}

def charge_info(api_key, charge_id):
    logging.critical("charge_info() called")
    headers = generate_headers(api_key)
    headers["Content-Type"] = "application/json"
    endpoint_url = "/v1/charge/" + charge_id
    query_url = base_url + endpoint_url
    logging.error(query_url)
    requests_response = requests.get(query_url, headers=headers)
    if requests_response.status_code == 200:
        logging.error(requests_response.json()) #debugging
        return requests_response.json()
    else:
        logging.error(requests_response.json()) #debugging
        return {"failed": "failed"}

def create_refund(api_key, charge_id, btc_refund_address, email_address):
    logging.critical("create_refund() called")
    headers = generate_headers(api_key)
    headers["Content-Type"] = "application/json"
    payload = {
        "checkout_id": charge_id, 
        "address": btc_refund_address, 
        "email": email_address}
    endpoint_url = "/v1/refunds"
    query_url = base_url + endpoint_url
    logging.error(query_url)
    requests_response = requests.post(query_url, data=json.dumps(payload), headers=headers)
    if requests_response.status_code == 200:
        logging.error(requests_response.json()) #debugging
        return requests_response.json()
    else:
        logging.error(requests_response.json()) #debugging
        return {"failed": "failed"}
