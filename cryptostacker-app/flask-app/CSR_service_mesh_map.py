service_mesh_map = {}

base_api_url_api_gateway_1 = "https://l09oxcjh8i.execute-api.us-east-2.amazonaws.com/prod/"

base_api_url_api_gateway_2 = "https://ni1vi4cobf.execute-api.us-east-2.amazonaws.com/prod/"

api_keys_read_write = "https://ni1vi4cobf.execute-api.us-east-2.amazonaws.com/prod/api-keys-read-write"

cron_events_sqs_queue = "https://sqs.us-east-2.amazonaws.com/370458797273/CRS-cron-events-dca-tf"

cryptostacker_logout_url = "https://www.cryptostacker.io/logged_out"

cryptostacker_logged_out_verify_email = "https://www.cryptostacker.io/logged_out_verify_email"

######################################################################################
#Auth0 - dev
#auth0_base_url = "https://dev-ky9kavap.us.auth0.com" 
#auth0_audience_url = "https://dev-ky9kavap.us.auth0.com" 
#auth0_base_logout_url = "https://dev-ky9kavap.us.auth0.com/v2/logout?returnTo=" 
#auth0_base_api_url = "https://dev-ky9kavap.us.auth0.com/api/v2/" 

#Auth0 - prod
#no cname
auth0_base_url = "https://cryptostacker.us.auth0.com" 
auth0_audience_url = "https://cryptostacker.us.auth0.com/api/v2/" 
auth0_base_logout_url = "https://cryptostacker.us.auth0.com/v2/logout?returnTo=" 
auth0_base_api_url = "https://cryptostacker.us.auth0.com/api/v2/" 

#cname
#login.cryptostacker.io
auth0_base_url_cname = "https://login.cryptostacker.io" 
auth0_audience_url_cname = "https://login.cryptostacker.io/api/v2/" 
auth0_base_logout_url_cname = "https://login.cryptostacker.io/v2/logout?returnTo=" 
auth0_base_api_url_cname = "https://login.cryptostacker.io/api/v2/" 
######################################################################################



######################################################################################
#Opennode
#Development - https://dev-checkout.opennode.com/ {id}
#Production - https://checkout.opennode.com/ {id}

#opennode_api_base_url = "https://dev-api.opennode.com" #dev
opennode_api_base_url = "https://api.opennode.com"     #prod

#opennode_hosted_checkout_base_url = "https://dev-checkout.opennode.com/" #dev
opennode_hosted_checkout_base_url = "https://checkout.opennode.com/"    #prod
######################################################################################


######################################################################################
#Persona
#persona_base_url = "https://withpersona.com"

persona_base_url = "https://cryptostacker.withpersona.com"
#persona_environment = "sandbox"
persona_environment = "production"
persona_template_id = "itmpl_4amq1Kc618uyLgzrbAipJeoU"


######################################################################################


api_kms_key = "894a17ed-80b7-4d33-886e-f33a7d975c27" #CSR-user-api-keys-backend-tf

users_api = base_api_url_api_gateway_1 + "users"

api_keys_write = base_api_url_api_gateway_1 + "api-keys-write"

api_keys_metadata = base_api_url_api_gateway_1 + "api-keys-metadata"

api_dca_schedule = base_api_url_api_gateway_1 + "dca-schedule"

api_dca_purchase_logs = base_api_url_api_gateway_1 + "dca-purchase-logs"

api_delete_users_everywhere = base_api_url_api_gateway_1 + "delete-user-everywhere"

api_pending_payments = base_api_url_api_gateway_1 + "pending-payments"

api_subscription_tier = base_api_url_api_gateway_1 + "subscription-tier"

api_pricing_tier = base_api_url_api_gateway_1 + "pricing-tier"

api_user_subscription_status = base_api_url_api_gateway_1 + "user-subscription-status"

api_user_payments = base_api_url_api_gateway_1 + "user-payments"

api_brand_ambassador_referral_codes = base_api_url_api_gateway_1 + "brand-ambassador-referral-codes"

api_failed_dca_counter = base_api_url_api_gateway_1 + "failed-dca-counter"

api_api_key_submission_counter = base_api_url_api_gateway_1 + "api-key-submission-counter"

api_resend_verification_email = base_api_url_api_gateway_1 + "resend-verification-email"

api_daily_user_metrics = base_api_url_api_gateway_1 + "daily-user-metrics"

api_refresh_kyc_verification_status_single_user = base_api_url_api_gateway_1 + "refresh-kyc-verification-status-single-user"

api_auth0_token_response = base_api_url_api_gateway_1 + "auth0-token-response"

api_opennode = base_api_url_api_gateway_1 + "opennode"

api_auth0 = base_api_url_api_gateway_1 + "auth0"

api_daily_revenue_metrics = base_api_url_api_gateway_1 + "daily-revenue-metrics"

service_mesh_map["api_keys_read_write"] = api_keys_read_write
service_mesh_map["cron_events_sqs_queue"] = cron_events_sqs_queue
service_mesh_map["api_kms_key"] = api_kms_key
service_mesh_map["users_api"] = users_api
service_mesh_map["api_keys_write"] = api_keys_write
service_mesh_map["api_keys_metadata"] = api_keys_metadata
service_mesh_map["api_dca_schedule"] = api_dca_schedule
service_mesh_map["api_dca_purchase_logs"] = api_dca_purchase_logs
service_mesh_map["api_delete_users_everywhere"] = api_delete_users_everywhere
service_mesh_map["api_pending_payments"] = api_pending_payments
service_mesh_map["api_subscription_tier"] = api_subscription_tier
service_mesh_map["api_pricing_tier"] = api_pricing_tier
service_mesh_map["api_user_subscription_status"] = api_user_subscription_status
service_mesh_map["api_user_payments"] = api_user_payments
service_mesh_map["api_brand_ambassador_referral_codes"] = api_brand_ambassador_referral_codes
service_mesh_map["api_failed_dca_counter"] = api_failed_dca_counter
service_mesh_map["api_api_key_submission_counter"] = api_api_key_submission_counter
service_mesh_map["api_resend_verification_email"] = api_resend_verification_email
service_mesh_map["api_daily_user_metrics"] = api_daily_user_metrics
service_mesh_map["api_refresh_kyc_verification_status_single_user"] = api_refresh_kyc_verification_status_single_user
service_mesh_map["api_auth0_token_response"] = api_auth0_token_response
service_mesh_map["api_opennode"] = api_opennode
service_mesh_map["api_daily_revenue_metrics"] = api_daily_revenue_metrics
