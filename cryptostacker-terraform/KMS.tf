
#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-lambda-env-var-tf" {
  description = "KMS key used to encrypt environment variables of lambdas"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-lambda-env-var-tf" {
  name          = "alias/CSR-lambda-env-var-tf"
  target_key_id = aws_kms_key.CSR-lambda-env-var-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR_one_proto_master-tf" {
  description = "One key to rule them all for TF prototype"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR_one_proto_master-tf" {
  name          = "alias/CSR_one_proto_master-tf"
  target_key_id = aws_kms_key.CSR_one_proto_master-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-primary-serverless-db-1-tf" {
  description = "Key to be used by serverless RDS DB"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-primary-serverless-db-1-tf" {
  name          = "alias/CSR-primary-serverless-db-1-tf"
  target_key_id = aws_kms_key.CSR-primary-serverless-db-1-tf.key_id
}

#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-primary-serverless-db-2-tf" {
  description = "Key to be used by serverless RDS DB"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-primary-serverless-db-2-tf" {
  name          = "alias/CSR-primary-serverless-db-2-tf"
  target_key_id = aws_kms_key.CSR-primary-serverless-db-2-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CRS-cron-events-dca-tf" {
  description = "Key to be used by cron job sqs queue"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CRS-cron-events-dca-tf" {
  name          = "alias/CRS-cron-events-dca-tf"
  target_key_id = aws_kms_key.CRS-cron-events-dca-tf.key_id
}



#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-crypto-payment-gateway-api-tf" {
  description = "Key to be used by secrets manager to encrypt the cryptocurrency payment gateway api keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-crypto-payment-gateway-api-tf" {
  name          = "alias/CSR-crypto-payment-gateway-api-tf"
  target_key_id = aws_kms_key.CSR-crypto-payment-gateway-api-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-fiat-payment-gateway-api-tf" {
  description = "Key to be used by secrets manager to encrypt the fiat payment gateway api keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-fiat-payment-gateway-api-tf" {
  name          = "alias/CSR-fiat-payment-gateway-api-tf"
  target_key_id = aws_kms_key.CSR-fiat-payment-gateway-api-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-user-api-keys-frontend-tf" {
  description = "Key to be used to encrypt user entered API keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-user-api-keys-frontend-tf" {
  name          = "alias/CSR-user-api-keys-frontend-tf"
  target_key_id = aws_kms_key.CSR-user-api-keys-frontend-tf.key_id
}

#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-user-api-keys-backend-tf" {
  description = "Key to be used to encrypt user entered API keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-user-api-keys-backend-tf" {
  name          = "alias/CSR-user-api-keys-backend-tf"
  target_key_id = aws_kms_key.CSR-user-api-keys-backend-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-auth0-api-keys-tf" {
  description = "Key to be used by secrets manager to encrypt Auth0 API keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-auth0-api-keys-tf" {
  name          = "alias/CSR-auth0-api-keys-tf"
  target_key_id = aws_kms_key.CSR-auth0-api-keys-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-auth0-api-keys-2-tf" {
  description = "Key to be used by secrets manager to encrypt Auth0 API keys"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-auth0-api-keys-2-tf" {
  name          = "alias/CSR-auth0-api-keys-2-tf"
  target_key_id = aws_kms_key.CSR-auth0-api-keys-2-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-redis-at-rest-encryption-tf" {
  description = "Key to be used by redis for at rest encryption"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-redis-at-rest-encryption-tf" {
  name          = "alias/CSR-redis-at-rest-encryption-tf"
  target_key_id = aws_kms_key.CSR-redis-at-rest-encryption-tf.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF" {
  description = "Key to be used for redis secret"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}

#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF" {
  name          = "alias/CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF"
  target_key_id = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF" {
  description = "Key to be used for app_secret secret"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF" {
  name          = "alias/CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF"
  target_key_id = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF.key_id
}

#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-opennode_api_key-TF" {
  description = "Key to be used for app_secret secret"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-opennode_api_key-TF" {
  name          = "alias/CSR-opennode_api_key-TF"
  target_key_id = aws_kms_key.CSR-opennode_api_key-TF.key_id
}

#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-sendgrid_api_key-TF" {
  description = "Key to be used for sendgrid api"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-sendgrid_api_key-TF" {
  name          = "alias/CSR-sendgrid_api_key-TF"
  target_key_id = aws_kms_key.CSR-sendgrid_api_key-TF.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-Service-Mesh-Secret_1-TF" {
  description = "Key to be used for service mesh secret #1"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-Service-Mesh-Secret_1-TF" {
  name          = "alias/CSR-Service-Mesh-Secret_1-TF"
  target_key_id = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
}


#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-Service-Mesh-Secret_2-TF" {
  description = "Key to be used for service mesh secret #2"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-Service-Mesh-Secret_2-TF" {
  name          = "alias/CSR-Service-Mesh-Secret_2-TF"
  target_key_id = aws_kms_key.CSR-Service-Mesh-Secret_2-TF.key_id
}

#CREATE KMS KEY(S) - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key#customer_master_key_spec
resource "aws_kms_key" "CSR-persona-secrets-TF" {
  description = "Key to be used for persona secrets"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  
  deletion_window_in_days = 30
  is_enabled = true
  enable_key_rotation = false
}
#create KMS alias - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias
resource "aws_kms_alias" "CSR-persona-secrets-TF" {
  name          = "alias/CSR-persona-secrets-TF"
  target_key_id = aws_kms_key.CSR-persona-secrets-TF.key_id
}
