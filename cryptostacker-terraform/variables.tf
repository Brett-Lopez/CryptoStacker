#export TF_VAR_db_username=<username> 
#export TF_VAR_db_password=<password>
### NO HYPENS ALLOWED IN ENVIRONMENT VARIABLES!! ### 

#export TF_VAR_primary_serverless_db_1_USERNAME_tf=<username>
variable "primary_serverless_db_1_USERNAME_tf" { #set value with environment var - https://learn.hashicorp.com/tutorials/terraform/sensitive-variables?in=terraform/configuration-language
  description = "Database administrator username"
  type        = string
  sensitive   = true
}

#export TF_VAR_primary_serverless_db_1_PASSWORD_tf=<PASSWORD>
variable "primary_serverless_db_1_PASSWORD_tf" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

#export TF_VAR_primary_serverless_db_2_USERNAME_tf=<username>
variable "primary_serverless_db_2_USERNAME_tf" { #set value with environment var - https://learn.hashicorp.com/tutorials/terraform/sensitive-variables?in=terraform/configuration-language
  description = "Database administrator username"
  type        = string
  sensitive   = true
}

#export TF_VAR_primary_serverless_db_2_PASSWORD_tf=<PASSWORD>
variable "primary_serverless_db_2_PASSWORD_tf" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}


#export TF_VAR_CSR_auth0_api_keys_tf_AUTH0_CLIENT_ID=<auth0_api_key_client_id>
variable "CSR_auth0_api_keys_tf_AUTH0_CLIENT_ID" { #set value with environment var - https://learn.hashicorp.com/tutorials/terraform/sensitive-variables?in=terraform/configuration-language
  description = "Auth0 api key"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_auth0_api_keys_tf_AUTH0_CLIENT_SECRET=<auth0_api_key_client_secret>
variable "CSR_auth0_api_keys_tf_AUTH0_CLIENT_SECRET" {
  description = "Auth0 api key"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_auth0_api_keys_tf_AUTH0_DISCOVERY_URL=<DISCOVERY_URL>
variable "CSR_auth0_api_keys_tf_AUTH0_DISCOVERY_URL" {
  description = "Auth0 discovery URL"
  type        = string
  default     = "https://login.cryptostacker.io/.well-known/openid-configuration"
  #sensitive   = true
}

#export TF_VAR_CSR_ECS_TASKS_WWW_WEBAPP_app_secret_key_TF=<Secret key used by flask sessions>
variable "CSR_ECS_TASKS_WWW_WEBAPP_app_secret_key_TF" {
  description = "Secret key used by flask sessions"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_Service_Mesh_Secret_1_TF=<Secret key used to authenticate the service mesh>
variable "CSR_Service_Mesh_Secret_1_TF" {
  description = "Secret key used to authenticate the service mesh"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_Service_Mesh_Secret_2_TF=<Secret key used to authenticate the service mesh>
variable "CSR_Service_Mesh_Secret_2_TF" {
  description = "Secret key used to authenticate the service mesh, read-write API"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_opennode_api_key_TF=<Secret key used to authenticate the service mesh>
variable "CSR_opennode_api_key_TF" {
  description = "Secret key used to authenticate against opennode api endpoints"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_SENDGRID_API_KEY_TF=<Secret key used to authenticate the service mesh>
variable "CSR_SENDGRID_API_KEY_TF" {
  description = "Secret key used to authenticate against sendgrid api endpoints"
  type        = string
  sensitive   = true
}


#export TF_VAR_CSR_persona_secrets_TF_api_secret=<persona_api_secret>
variable "CSR_persona_secrets_TF_api_secret" {
  description = "persona secrets"
  type        = string
  sensitive   = true
}

#export TF_VAR_CSR_persona_secrets_TF_template_id=<persona_template_id>
variable "CSR_persona_secrets_TF_template_id" {
  description = "persona secrets"
  type        = string
  default     = "itmpl_4amq1Kc618uyLgzrbAipJeoU" #exposed in the frontend, not a secret
}

variable "AWS_REGION" {
  description = "AWS Region to be used"
  type        = string
  default     = "us-east-2"
}
