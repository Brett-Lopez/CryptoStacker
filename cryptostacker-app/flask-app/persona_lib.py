#https://docs.withpersona.com/docs/quickstart-hosted-flow
#https://docs.withpersona.com/reference/list-all-inquiries

import requests
import CSR_service_mesh_map
import CSR_toolkit
import json
import datetime
import urllib.parse
import logging
import hashlib
from email.utils import formatdate
import base64
import hmac


def retrieve_inquiry_by_uuid(api_secret, persona_uuid):
    header = {
        "Accept": "application/json",
        "Persona-Version": "2021-05-14",
        "Authorization": "Bearer " + str(api_secret)
    }
    #query_url = "https://withpersona.com/api/v1/inquiries" 
    query_url = CSR_service_mesh_map.persona_base_url + "/api/v1/inquiries" + "?filter[reference-id]=" + persona_uuid
    inquery_by_uuid_response = requests.get(query_url, headers=header)
    return inquery_by_uuid_response
    