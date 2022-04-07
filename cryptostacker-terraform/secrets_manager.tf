#set policy for each secret - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_policy
#set secret string for each secret as applicable - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version
#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-primary-serverless-db-1-tf" {
  name = "CSR-primary-serverless-db-1-tf"
  kms_key_id = aws_kms_key.CSR-primary-serverless-db-1-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-primary-serverless-db-2-tf" {
  name = "CSR-primary-serverless-db-2-tf"
  kms_key_id = aws_kms_key.CSR-primary-serverless-db-2-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-crypto-payment-gateway-api-tf" {
  name = "CSR-crypto-payment-gateway-api-tf"
  kms_key_id = aws_kms_key.CSR-crypto-payment-gateway-api-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-fiat-payment-gateway-api-tf" {
  name = "CSR-fiat-payment-gateway-api-tf"
  kms_key_id = aws_kms_key.CSR-fiat-payment-gateway-api-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-auth0-api-keys-tf" {
  name = "CSR-auth0-api-keys-tf"
  kms_key_id = aws_kms_key.CSR-auth0-api-keys-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-auth0-api-keys-2-tf" {
  name = "CSR-auth0-api-keys-2-tf"
  kms_key_id = aws_kms_key.CSR-auth0-api-keys-2-tf.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF" {
  name = "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF"
  kms_key_id = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF" {
  name = "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF"
  kms_key_id = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-opennode_api_key-TF" {
  name = "CSR-opennode_api_key-TF"
  kms_key_id = aws_kms_key.CSR-opennode_api_key-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-sendgrid_api_key-TF" {
  name = "CSR-sendgrid_api_key-TF"
  kms_key_id = aws_kms_key.CSR-sendgrid_api_key-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-Service-Mesh-Secret_1-TF" {
  name = "CSR-Service-Mesh-Secret_1-TF"
  kms_key_id = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-Service-Mesh-Secret_2-TF" {
  name = "CSR-Service-Mesh-Secret_2-TF"
  kms_key_id = aws_kms_key.CSR-Service-Mesh-Secret_2-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}

#secrets manager - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "CSR-persona-secrets-TF" {
  name = "CSR-persona-secrets-TF"
  kms_key_id = aws_kms_key.CSR-persona-secrets-TF.key_id #- (Optional) ARN or Id of the AWS KMS 
  #policy = #prod set policy - (Optional) Valid JSON document representing a resource policy. 
  recovery_window_in_days = 30
}



#set secret value
resource "aws_secretsmanager_secret_version" "CSR-primary-serverless-db-1-tf" {
  secret_id     = aws_secretsmanager_secret.CSR-primary-serverless-db-1-tf.id
  secret_string = <<EOF
{
"username": "${var.primary_serverless_db_1_USERNAME_tf}",
"password": "${var.primary_serverless_db_1_PASSWORD_tf}",
"engine": "aurora-mysql",
"host": "primary-serverless-db-1-tf.cluster-cjgcgv2wdtfs.us-east-2.rds.amazonaws.com",
"port": 3306
}
EOF
}

#set secret value
resource "aws_secretsmanager_secret_version" "CSR-primary-serverless-db-2-tf" {
  secret_id     = aws_secretsmanager_secret.CSR-primary-serverless-db-2-tf.id
  secret_string = <<EOF
{
"username": "${var.primary_serverless_db_2_USERNAME_tf}",
"password": "${var.primary_serverless_db_2_PASSWORD_tf}",
"engine": "aurora-mysql",
"host": "primary-serverless-db-2-tf.cluster-cjgcgv2wdtfs.us-east-2.rds.amazonaws.com",
"port": 3306
}
EOF
}


#CSR-auth0-api-keys-tf
resource "aws_secretsmanager_secret_version" "CSR-auth0-api-keys-tf" {
  secret_id     = aws_secretsmanager_secret.CSR-auth0-api-keys-tf.id
  secret_string = <<EOF
{
"AUTH0_CLIENT_ID": "${var.CSR_auth0_api_keys_tf_AUTH0_CLIENT_ID}",
"AUTH0_DISCOVERY_URL": "${var.CSR_auth0_api_keys_tf_AUTH0_DISCOVERY_URL}"
}
EOF
}

#CSR-auth0-api-keys-tf
resource "aws_secretsmanager_secret_version" "CSR-auth0-api-keys-2-tf" {
  secret_id     = aws_secretsmanager_secret.CSR-auth0-api-keys-2-tf.id
  secret_string = <<EOF
{
"AUTH0_CLIENT_ID": "${var.CSR_auth0_api_keys_tf_AUTH0_CLIENT_ID}",
"AUTH0_CLIENT_SECRET": "${var.CSR_auth0_api_keys_tf_AUTH0_CLIENT_SECRET}",
"AUTH0_DISCOVERY_URL": "${var.CSR_auth0_api_keys_tf_AUTH0_DISCOVERY_URL}"
}
EOF
}

#redis primary_endpoint_address - CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF
resource "aws_secretsmanager_secret_version" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.id
  secret_string = <<EOF
{
"primary_endpoint_address": "${aws_elasticache_replication_group.CSR-flask-session-redis-tf.primary_endpoint_address}:6379"
}
EOF
}

#flask app.secret_key - CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF
resource "aws_secretsmanager_secret_version" "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF.id
  secret_string = <<EOF
{
"app_secret_key": "${var.CSR_ECS_TASKS_WWW_WEBAPP_app_secret_key_TF}"
}
EOF
}

#Secret key used to authenticate against opennode api endpoints
resource "aws_secretsmanager_secret_version" "CSR-opennode_api_key-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-opennode_api_key-TF.id
  secret_string = <<EOF
{
"api_key": "${var.CSR_opennode_api_key_TF}"
}
EOF
}

#Secret key used to authenticate against sendgrid api endpoints
resource "aws_secretsmanager_secret_version" "CSR-sendgrid_api_key-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-sendgrid_api_key-TF.id
  secret_string = <<EOF
{
"SENDGRID_API_KEY": "${var.CSR_SENDGRID_API_KEY_TF}"
}
EOF
}

#service mesh auth #1 - CSR-Service-Mesh-Secret_1-TF
resource "aws_secretsmanager_secret_version" "CSR-Service-Mesh-Secret_1-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-Service-Mesh-Secret_1-TF.id
  secret_string = <<EOF
{
"CSR_Service_Mesh_Secret_1": "${var.CSR_Service_Mesh_Secret_1_TF}"
}
EOF
}

#service mesh auth #2 - CSR-Service-Mesh-Secret_2-TF
resource "aws_secretsmanager_secret_version" "CSR-Service-Mesh-Secret_2-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-Service-Mesh-Secret_2-TF.id
  secret_string = <<EOF
{
"CSR_Service_Mesh_Secret_2": "${var.CSR_Service_Mesh_Secret_2_TF}"
}
EOF
}


#CSR-persona-secrets-TF
resource "aws_secretsmanager_secret_version" "CSR-persona-secrets-TF" {
  secret_id     = aws_secretsmanager_secret.CSR-persona-secrets-TF.id
  secret_string = <<EOF
{
"persona_api_secret": "${var.CSR_persona_secrets_TF_api_secret}",
"persona_template_id": "${var.CSR_persona_secrets_TF_template_id}"
}
EOF
}
