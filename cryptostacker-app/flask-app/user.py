from flask_login import UserMixin
import requests
import CSR_service_mesh_map
import logging

API_GATEWAY_URL = CSR_service_mesh_map.users_api + "?identity_provider_sub_id="

class User(UserMixin):
    def __init__(self, id_, first_name, last_name, email, email_verified, time_created_epoch=None, user_id=None, provider_name=None, 
    timezone="None", geo_location="None", last_login_epoch="None", brand_ambassador="False", site_metrics_viewer="False", site_admin_full="False",
    persona_user_id="NULL", persona_verification_status="1"):
        logging.critical("user model __init__() called") #debugging
        self.user_id = user_id
        self.id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.email_verified = email_verified
        self.time_created_epoch = time_created_epoch
        self.provider_name = provider_name
        self.timezone = timezone
        self.geo_location = geo_location
        self.last_login_epoch = last_login_epoch
        self.brand_ambassador = brand_ambassador
        self.site_metrics_viewer = site_metrics_viewer
        self.site_admin_full = site_admin_full
        self.persona_user_id = persona_user_id
        self.persona_verification_status = persona_verification_status
        
    @staticmethod
    def get(identity_provider_sub_id, api_gateway_api_key):
        logging.critical("user model get() called") #debugging
        headers = {}
        headers["X-API-Key"] = api_gateway_api_key
        api_get_response = requests.get(API_GATEWAY_URL + str(identity_provider_sub_id), headers=headers)
        api_get_response_json = api_get_response.json()
        logging.error(api_get_response_json) #debugging
        if api_get_response_json == "None":
            return None

        user = User(
            id_=api_get_response_json[1], 
            first_name=api_get_response_json[3], last_name=api_get_response_json[4], 
            email=api_get_response_json[5], email_verified=api_get_response_json[6], 
            time_created_epoch=api_get_response_json[10], user_id=api_get_response_json[0],
            provider_name=api_get_response_json[2], timezone=api_get_response_json[7], 
            geo_location=api_get_response_json[8], last_login_epoch=api_get_response_json[9],
            brand_ambassador=api_get_response_json[11], site_metrics_viewer=api_get_response_json[12], 
            site_admin_full=api_get_response_json[13], persona_user_id=api_get_response_json[14],
            persona_verification_status=api_get_response_json[15]
        )
        return user

    @staticmethod
    def create(identity_provider_sub_id, first_name, last_name, email, email_verified, api_gateway_api_key, provider_name=None):
        logging.critical("user model create() called") #debugging
        headers = {}
        headers["X-API-Key"] = api_gateway_api_key
        api_get_response = requests.post(API_GATEWAY_URL + str(identity_provider_sub_id) + "&" + "first_name" + "=" + str(first_name) +
        "&" + "last_name" + "=" + str(last_name) + "&" + "email_address" + "=" + str(email) + "&" + "email_verified" + "=" + str(email_verified)
        + "&" + "identity_provider" + "=" + str(provider_name), headers=headers)

    
    @staticmethod
    def update(identity_provider_sub_id, first_name, last_name, email, email_verified, api_gateway_api_key, provider_name=None):
        logging.critical("user model update() called") #debugging
        headers = {}
        headers["X-API-Key"] = api_gateway_api_key
        api_get_response = requests.post(API_GATEWAY_URL + str(identity_provider_sub_id) + "&" + "first_name" + "=" + str(first_name) +
        "&" + "last_name" + "=" + str(last_name) + "&" + "email_address" + "=" + str(email) + "&" + "email_verified" + "=" + str(email_verified)
        + "&" + "identity_provider" + "=" + str(provider_name) + "&update=standard", headers=headers)

    
    @staticmethod
    def update_without_names(identity_provider_sub_id, email, email_verified, api_gateway_api_key, provider_name=None):
        logging.critical("user model update_without_names() called") #debugging
        headers = {}
        headers["X-API-Key"] = api_gateway_api_key
        api_get_response = requests.post(API_GATEWAY_URL + str(identity_provider_sub_id) +
        "&email_address=" + str(email) + "&email_verified=" + str(email_verified) +
        "&identity_provider=" + str(provider_name) + "&update=emailandlogin", headers=headers)

        