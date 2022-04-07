import requests
import CSR_service_mesh_map
import CSR_toolkit
import json
import datetime
import urllib.parse
import logging

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

#https://auth0.com/docs/users/manage-users-using-the-management-api
#https://auth0.com/docs/api/management/v2
#scopes: 
# read:users 
# read:user_idp_tokens 
# update:users 
# update:users_app_metadata
# delete:users
# create:user_tickets

def get_bearer_token(client_id, client_secret):
    logging.critical("get_bearer_token() called")
    """
    input: auth0 client_id & client_secret
    output: bearer token
    """
    client_id_encoded = urllib.parse.quote_plus(client_id)
    client_secret_encoded = urllib.parse.quote_plus(client_secret)
    audience = CSR_service_mesh_map.auth0_audience_url
    audience_encoded = urllib.parse.quote_plus(audience)
    payload = "grant_type=client_credentials&client_id=" + client_id_encoded + "&client_secret=" + client_secret_encoded + "&audience=" + audience_encoded
    headers = { 'content-type': "application/x-www-form-urlencoded" }
    #query_url = "https://dev-ky9kavap.us.auth0.com/oauth/token"
    query_url = CSR_service_mesh_map.auth0_base_url + "/oauth/token"
    response_req = requests.post(query_url, data=payload, headers=headers) 
    logging.error(response_req.status_code) #debugging
    return response_req.json()["access_token"]

def convert_identity_provider_sub_id_TO_user_id_and_provider(identity_provider_sub_id):
    logging.critical("convert_identity_provider_sub_id_TO_user_id_and_provider() called")
    """
    input: identity_provider_sub_id
    output: tuple of provider & user_id
    """
    logging.error(identity_provider_sub_id.split("|"))
    provider = identity_provider_sub_id.split("|")[0]
    user_id = identity_provider_sub_id.split("|")[1]
    logging.error(provider)
    logging.error(user_id)
    return provider, user_id

def getauser(identity_provider_sub_id, access_token):
    """
    input:
    output: no output
    """
    logging.critical("getauser() called")
    #https://auth0.com/docs/api/management/v2#!/Users/get_users_by_id
    #get /api/v2/users/{id}
    #scopes:
    # read:users 
    # read:user_idp_tokens 
    identity_provider_sub_id_encoded = urllib.parse.quote_plus(identity_provider_sub_id)
    headers = {"Authorization": "Bearer " + access_token}
    query_url = CSR_service_mesh_map.auth0_base_api_url + "users/" + identity_provider_sub_id_encoded
    get_user_response = requests.get(query_url, headers=headers)
    logging.error(get_user_response.status_code)
    logging.error(get_user_response.json())

def blockuser(identity_provider_sub_id, access_token):
    """
    input:
    output:
    """
    logging.critical("blockuser() called")
    #https://auth0.com/docs/api/management/v2#!/Users/patch_users_by_id
    #patch /api/v2/users/{id}
    #Scopes:
    # update:users 
    # update:users_app_metadata
    identity_provider_sub_id_encoded = urllib.parse.quote_plus(identity_provider_sub_id)
    headers = {"Authorization": "Bearer " + access_token}
    query_url = CSR_service_mesh_map.auth0_base_api_url + "users/" + identity_provider_sub_id_encoded
    payload = {"blocked": "true"}
    block_user_response = requests.patch(query_url, data=payload, headers=headers)
    logging.error(block_user_response.status_code)
    logging.error(block_user_response.json())

def deleteuser(identity_provider_sub_id, access_token):
    """
    input:
    output:
    """
    logging.critical("deleteuser() called")
    #https://auth0.com/docs/api/management/v2#!/Users/delete_users_by_id
    #delete /api/v2/users/{id}
    #Scopes:
    # delete:users
    identity_provider_sub_id_encoded = urllib.parse.quote_plus(identity_provider_sub_id)
    headers = {"Authorization": "Bearer " + access_token}
    query_url = CSR_service_mesh_map.auth0_base_api_url + "users/" + identity_provider_sub_id_encoded
    delete_user_response = requests.delete(query_url, headers=headers)
    logging.error(delete_user_response.status_code)
    if delete_user_response.status_code == 204:
        return "success"
    else:
        return "failed"
    #204 	User successfully deleted.
    #400 	Invalid request URI. The message will vary depending on the cause.
    #401 	Invalid token.
    #401 	Client is not global.
    #401 	Invalid signature received for JSON Web Token validation.
    #403 	User to be acted on does not match subject in bearer token.
    #403 	Insufficient scope; expected any of: delete:users,delete:current_user.
    #429 	Too many requests. Check the X-RateLimit-Limit, X-RateLimit-Remaining and X-RateLimit-Reset headers.

def reset_google_mfa(identity_provider_sub_id, access_token):
    """
    input:
    output:
    """
    logging.critical("reset_mfa() called")
    #https://auth0.com/docs/api/management/v2#!/Users/delete_authenticators
    #As an admin, you can also use the Management API to delete a user's MFA enrollment using DELETE /api/v2/guardian/enrollments/{id}. This requires getting the enrollment ID first with a GET to the /get_enrollments endpoint. If the user has more than one enrollment, you will need to repeat the process for each enrollment.

    #Scopes:
    # delete:guardian_enrollments
    identity_provider_sub_id_encoded = urllib.parse.quote_plus(identity_provider_sub_id)
    headers = {"Authorization": "Bearer " + access_token}
    #query_url = CSR_service_mesh_map.auth0_base_api_url + "users/" + identity_provider_sub_id_encoded + "/multifactor/google-authenticator"
    query_url = CSR_service_mesh_map.auth0_base_api_url + "users/" + identity_provider_sub_id_encoded + "/authenticators"
    #delete /api/v2/users/{id}/authenticators 

    logging.error(query_url)
    delete_user_response = requests.delete(query_url, headers=headers)
    logging.error(delete_user_response.status_code)
    logging.error(delete_user_response)
    try:
        logging.error(delete_user_response.json())
    except:
        pass
    if delete_user_response.status_code == 204:
        return "success"
    else:
        return "failed"

    #204 	Multi-factor provider successfully deleted for user.
    #400 	Invalid request URI. The message will vary depending on the cause.
    #401 	Invalid token.
    #401 	Client is not global.
    #401 	Invalid signature received for JSON Web Token validation.
    #403 	User to be acted on does not match subject in bearer token.
    #403 	Insufficient scope; expected any of: update:users.
    #404 	User not found.
    #429 	Too many requests. Check the X-RateLimit-Limit, X-RateLimit-Remaining and X-RateLimit-Reset headers.
#    #https://login.auth0.com/api/v2/users/auth0%7C61bcc1de1e13dd0068c33cad/multifactor/google-authenticator

def change_password(identity_provider_sub_id, access_token):
    """
    input:
    output:
    """
    logging.critical("reset_password() called")
    #https://auth0.com/docs/api/management/v2#!/Users/patch_users_by_id

def generate_verification_link(identity_provider_sub_id, access_token):
    """
    input: identity_provider_sub_id, access_token
    output: string - https link used for verifying email address {'ticket': 'https://dev-ky9kavap.us.auth0.com/u/email-verification?ticket=1vqGdz9QTKC5OllFuH6eRHqAYFJsrO6m#'}
    """
    logging.critical("generate_verification_link() called")
    #https://auth0.com/docs/api/management/v2#!/Tickets/post_email_verification
    #post /api/v2/tickets/email-verification
    #Scopes
    # create:user_tickets
    request_body = {
      "result_url": "https://www.cryptostacker.io/login",
      "user_id": str(identity_provider_sub_id),
      "ttl_sec": 0, #Number of seconds for which the ticket is valid before expiration. If unspecified or set to 0, this value defaults to 432000 seconds (5 days)
      "includeEmailInRedirect": False
        }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
        }

    query_url = CSR_service_mesh_map.auth0_base_api_url + "tickets/email-verification"
    response_req = requests.post(query_url, data=json.dumps(request_body), headers=headers)
    print(response_req)
    print(response_req.status_code)
    print(response_req.json())
    if response_req.status_code >= 200 and response_req.status_code < 300:
        return str(response_req.json()["ticket"])
    else:
        return "failed"
