#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_resource
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_stage
#https://aws.amazon.com/premiumsupport/knowledge-center/api-gateway-troubleshoot-403-forbidden/


##############################################
## CSR_mysql_API_1-tf - api gateway - begins
##############################################

resource "aws_api_gateway_rest_api" "CSR_mysql_API_1-tf" {
  name        = "CSR_mysql_API_1-tf"
  description = "One API gateway to rule them all"
  endpoint_configuration {
    types = ["PRIVATE"]
    vpc_endpoint_ids = [
      aws_vpc_endpoint.api_gateway_endpoint_private_subnet-tf.id
    ]
  }
}

resource "aws_api_gateway_rest_api_policy" "CSR_mysql_API_1_policy-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "execute-api:/*"
            ]
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "execute-api:/*"
            ],
            "Condition" : {
                "StringNotEquals": {
                   "aws:SourceVpc": "${module.vpc.vpc_id}"
                }
            }
        }
    ]
}
EOF
}

#deployment is for all endpoints
resource "aws_api_gateway_deployment" "CSR_mysql_API_1-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id

  triggers = {
    redeployment = sha1(timestamp())
  }

  lifecycle {
    create_before_destroy = true
  }
}

#stage is for all of the endpoints
resource "aws_api_gateway_stage" "CSR_mysql_API_1_prod-tf" {
  deployment_id = aws_api_gateway_deployment.CSR_mysql_API_1-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  stage_name    = "prod"
}


##########################################
## api keys / auth headers - begin
##########################################
resource "aws_api_gateway_api_key" "CSR_mysql_api_1_key_1" {
  name = "CSR_mysql_api_1_key_1"
  enabled = true
  value = var.CSR_Service_Mesh_Secret_1_TF
  #expected length of value to be in the range (30 - 128)
}

resource "aws_api_gateway_usage_plan" "CSR-default" {
  name = "CSR-default"

  api_stages {
    api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
    stage  = aws_api_gateway_stage.CSR_mysql_API_1_prod-tf.stage_name
  }
  
  throttle_settings {
    burst_limit = 6000
    rate_limit  = 5000
  }
}

resource "aws_api_gateway_usage_plan_key" "CSR_mysql_api_1_key_1" {
  key_id        = aws_api_gateway_api_key.CSR_mysql_api_1_key_1.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.CSR-default.id
}
##########################################
## api keys / auth headers - end
##########################################



########################################
#CSR_mysql_API_1 - users resource begins
########################################
resource "aws_api_gateway_resource" "CSR_mysql_API_1_users-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "users"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_users_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_users_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_users_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_users_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_users_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-users-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-users-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_users_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_users_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-users-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-users-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_users_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_users_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-users-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-users-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_users_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_users_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_users_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_users_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_users_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_users-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_users_delete-tf.http_method
  status_code = "200"
}

######################################
#CSR_mysql_API_1 - users resource ends
######################################


###############################################
# CSR_mysql_API_1 - dca-schedule resource begin
###############################################
resource "aws_api_gateway_resource" "CSR_mysql_API_1_dca-schedule-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "dca-schedule"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_dca-schedule_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_dca-schedule_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_dca-schedule_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_dca-schedule_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-dca-schedule-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_dca-schedule_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_dca-schedule_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-dca-schedule-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_dca-schedule_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_dca-schedule_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_dca-schedule_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_dca-schedule-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_dca-schedule_post-tf.http_method
  status_code = "200"
}

##############################################
# CSR_mysql_API_1 - dca-schedule resource ends
##############################################


########################################################
# CSR_mysql_API_1 - api-keys-write resource begin
########################################################
resource "aws_api_gateway_resource" "CSR_mysql_API_1_api-keys-write-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "api-keys-write"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

#resource "aws_api_gateway_method" "CSR_mysql_API_1_api-keys-write_get-tf" {
#  authorization = "NONE"
#  http_method   = "GET"
#  api_key_required = true
#  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_api-keys-write-tf.id
#  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
#  
#}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-keys-write_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_api-keys-write-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-keys-write_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_api-keys-write-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-keys-write_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-keys-write-only-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-keys-write-only-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-keys-write_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_api-keys-write-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-keys-write_post-tf.http_method
  status_code = "200"
}

########################################################
# CSR_mysql_API_1 - api-keys-write resource ends
########################################################


########################################################
# CSR_mysql_API_1 - api-keys-metadata resource begin
########################################################

resource "aws_api_gateway_resource" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "api-keys-metadata"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-keys-metadata_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-keys-metadata_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-keys-metadata_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-keys-metadata_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-keys-metadata-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-keys-metadata_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-keys-metadata_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-keys-metadata-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-keys-metadata_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-keys-metadata_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-keys-metadata_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR-api-keys-metadata-api-gateway-lambda-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-keys-metadata_post-tf.http_method
  status_code = "200"
}

########################################################
# CSR_mysql_API_1 - api-keys-metadata resource end
########################################################


########################################################
# CSR_mysql_API_1 - dca-purchase-logs resource begins
########################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_dca-purchase-logs-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "dca-purchase-logs"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_dca-purchase-logs_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_dca-purchase-logs_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_dca-purchase-logs_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_dca-purchase-logs_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_dca-purchase-logs_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_dca-purchase-logs_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-dca-purchase-logs-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_dca-purchase-logs_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_dca-purchase-logs_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_dca-purchase-logs_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_dca-purchase-logs-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_dca-purchase-logs_delete-tf.http_method
  status_code = "200"
}

########################################################
# CSR_mysql_API_1 - dca-purchase-logs resource ends
########################################################


######################################################################
# CSR_mysql_API_1 - delete-user-everywhere resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_delete-user-everywhere-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "delete-user-everywhere"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_delete-user-everywhere_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_delete-user-everywhere_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_delete-user-everywhere_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_delete-user-everywhere_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_delete-user-everywhere_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_delete-user-everywhere_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-delete-user-everywhere-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_delete-user-everywhere_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_delete-user-everywhere_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_delete-user-everywhere_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_delete-user-everywhere-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_delete-user-everywhere_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - delete-user-everywhere resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - pending-payments resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_pending-payments-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "pending-payments"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pending-payments_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pending-payments_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pending-payments_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pending-payments_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pending-payments_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pending-payments_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pending-payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pending-payments_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pending-payments_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pending-payments_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pending-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pending-payments_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - pending-payments resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - user-subscription-status resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_user-subscription-status-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "user-subscription-status"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-subscription-status_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-subscription-status_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-subscription-status_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-subscription-status_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-subscription-status_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-subscription-status_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_subscription_status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-subscription-status_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-subscription-status_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-subscription-status_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-subscription-status-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-subscription-status_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - user-subscription-status resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - user-payments resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_user-payments-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "user-payments"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-payments_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-payments_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_user-payments_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-payments_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-payments_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-payments_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-payments_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_user-payments_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_user-payments_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-user_payments-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-payments_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-payments_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-payments_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-payments_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_user-payments_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_user-payments-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_user-payments_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - user-payments resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - subscription-tier resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_subscription-tier-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "subscription-tier"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_subscription-tier_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_subscription-tier_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_subscription-tier_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_subscription-tier_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_subscription-tier_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_subscription-tier_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-subscription_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_subscription-tier_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_subscription-tier_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_subscription-tier_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_subscription-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_subscription-tier_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - subscription-tier resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - pricing-tier resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_pricing-tier-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "pricing-tier"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pricing-tier_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pricing-tier_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_pricing-tier_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pricing-tier_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pricing-tier_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_pricing-tier_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-pricing_tier-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pricing-tier_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pricing-tier_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_pricing-tier_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_pricing-tier-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_pricing-tier_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - pricing-tier resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - brand-ambassador-referral-codes resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_brand-ambassador-referral-codes-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "brand-ambassador-referral-codes"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_brand-ambassador-referral-codes_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_brand-ambassador-referral-codes_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_brand-ambassador-referral-codes_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_brand-ambassador-referral-codes_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_brand-ambassador-referral-codes_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_brand-ambassador-referral-codes_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_brand-ambassador-referral-codes_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_brand-ambassador-referral-codes_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_brand-ambassador-referral-codes_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_brand-ambassador-referral-codes-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_brand-ambassador-referral-codes_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - brand-ambassador-referral-codes resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - failed-dca-counter resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_failed-dca-counter-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "failed-dca-counter"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_failed-dca-counter_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_failed-dca-counter_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_failed-dca-counter_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_failed-dca-counter_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_failed-dca-counter_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_failed-dca-counter_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-failed-dca-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_failed-dca-counter_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_failed-dca-counter_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_failed-dca-counter_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_failed-dca-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_failed-dca-counter_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - failed-dca-counter resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - auth0-token-response resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_auth0-token-response-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "auth0-token-response"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0-token-response_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0-token-response_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0-token-response_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0-token-response_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0-token-response_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0-token-response_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-token-response-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0-token-response_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0-token-response_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0-token-response_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-token-response-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0-token-response_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - auth0-token-response resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - auth0 resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_auth0-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "auth0"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_auth0_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-api-gateway-lambda-tf.invoke_arn
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_auth0_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_auth0_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-auth0-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_auth0_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_auth0-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_auth0_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - auth0 resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - opennode resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_opennode-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "opennode"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_opennode_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_opennode_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_opennode_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_opennode_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_opennode_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-opennode-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_opennode_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_opennode_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-opennode-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_opennode_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_opennode_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-opennode-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_opennode_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_opennode_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_opennode_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_opennode_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_opennode_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_opennode-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_opennode_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - opennode resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - api-key-submission-counter resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_api-key-submission-counter-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "api-key-submission-counter"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-key-submission-counter_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-key-submission-counter_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_api-key-submission-counter_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-key-submission-counter_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-key-submission-counter_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_api-key-submission-counter_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-key-submission-counter-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-key-submission-counter_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-key-submission-counter_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_api-key-submission-counter_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_api-key-submission-counter-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_api-key-submission-counter_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - api-key-submission-counter resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - daily-user-metrics resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_daily-user-metrics-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "daily-user-metrics"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-user-metrics_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-user-metrics_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-user-metrics_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-user-metrics_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-user-metrics_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-user-metrics_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-user-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-user-metrics_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-user-metrics_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-user-metrics_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-user-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-user-metrics_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - daily-user-metrics resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - daily-revenue-metrics resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_daily-revenue-metrics-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "daily-revenue-metrics"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-revenue-metrics_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-revenue-metrics_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_daily-revenue-metrics_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-revenue-metrics_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-revenue-metrics_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_daily-revenue-metrics_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-daily-revenue-metrics-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-revenue-metrics_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-revenue-metrics_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_daily-revenue-metrics_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_daily-revenue-metrics-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_daily-revenue-metrics_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - daily-revenue-metrics resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - resend-verification-email resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_resend-verification-email-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "resend-verification-email"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_resend-verification-email_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_resend-verification-email-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_resend-verification-email_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_resend-verification-email-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_resend-verification-email_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-resend-verification-email-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-resend-verification-email-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_resend-verification-email_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_resend-verification-email-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_resend-verification-email_post-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - resend-verification-email resource ends
######################################################################


######################################################################
# CSR_mysql_API_1 - refresh-kyc-verification-status-single-user resource begins
######################################################################

resource "aws_api_gateway_resource" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "refresh-kyc-verification-status-single-user"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_delete-tf" {
  authorization = "NONE"
  http_method   = "DELETE"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_integration_delete-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_delete-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_post-tf.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_1_refresh-kyc-verification-status-single-user_200_response_delete-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_1_refresh-kyc-verification-status-single-user-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_1_refresh-kyc-verification-status-single-user_delete-tf.http_method
  status_code = "200"
}

######################################################################
# CSR_mysql_API_1 - refresh-kyc-verification-status-single-user resource ends
######################################################################



resource "aws_api_gateway_resource" "CSR_mysql_API_1_user-behavior-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "user-behavior"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_resource" "CSR_mysql_API_1_pending-payments-counter-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "pending-payments-counter"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}

resource "aws_api_gateway_resource" "CSR_mysql_API_1_general-error-log-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.root_resource_id
  path_part   = "general-error-log"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_1-tf.id
}


##############################################
## CSR_mysql_API_1-tf - api gateway - ends
##############################################


##############################################
## CSR_mysql_API_2-tf - api gateway - begins
##############################################


resource "aws_api_gateway_rest_api" "CSR_mysql_API_2-tf" {
  name        = "CSR_mysql_API_2-tf"
  description = "One API gateway to rule them all"
  endpoint_configuration {
    types = ["PRIVATE"]
    vpc_endpoint_ids = [
      aws_vpc_endpoint.api_gateway_endpoint_private_subnet-tf.id
    #  aws_vpc_endpoint.api_gateway_endpoint_public_subnet-tf.id,
    #  aws_vpc_endpoint.api_gateway_endpoint_database_subnet-tf.id
    ]
  }
}

resource "aws_api_gateway_rest_api_policy" "CSR_mysql_API_2_policy-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "execute-api:/*"
            ]
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "execute-api:/*"
            ],
            "Condition" : {
                "StringNotEquals": {
                   "aws:SourceVpc": "${module.vpc.vpc_id}"
                }
            }
        }
    ]
}
EOF
}

#deployment is for all endpoints
resource "aws_api_gateway_deployment" "CSR_mysql_API_2-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id

  triggers = {
    redeployment = sha1(timestamp())
  }

  lifecycle {
    create_before_destroy = true
  }
}

#stage is for all of the endpoints
resource "aws_api_gateway_stage" "CSR_mysql_API_2_prod-tf" {
  deployment_id = aws_api_gateway_deployment.CSR_mysql_API_2-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  stage_name    = "prod"
}


############################################
### api keys / auth headers - begin ########
############################################
resource "aws_api_gateway_api_key" "CSR_mysql_API_2_key_1" {
  name = "CSR_mysql_API_2_key_1"
  enabled = true
  value = var.CSR_Service_Mesh_Secret_2_TF
  #expected length of value to be in the range (30 - 128)
}

resource "aws_api_gateway_usage_plan" "CSR-mysql_API_2" {
  name = "mysql_API_2"

  api_stages {
    api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
    stage  = aws_api_gateway_stage.CSR_mysql_API_2_prod-tf.stage_name
  }
  
  throttle_settings {
    burst_limit = 6000
    rate_limit  = 5000
  }
}

resource "aws_api_gateway_usage_plan_key" "CSR_mysql_API_2_key_1" {
  key_id        = aws_api_gateway_api_key.CSR_mysql_API_2_key_1.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.CSR-mysql_API_2.id
}
##########################################
### api keys / auth headers - end ########
##########################################


############################################################
### CSR_mysql_API_2 - api-keys-read-write resource begin ###
############################################################
resource "aws_api_gateway_resource" "CSR_mysql_API_2_api-keys-read-write-tf" {
  parent_id   = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.root_resource_id
  path_part   = "api-keys-read-write"
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
}

resource "aws_api_gateway_method" "CSR_mysql_API_2_api-keys-read-write_get-tf" {
  authorization = "NONE"
  http_method   = "GET"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  
}

resource "aws_api_gateway_method" "CSR_mysql_API_2_api-keys-read-write_post-tf" {
  authorization = "NONE"
  http_method   = "POST"
  api_key_required = true
  resource_id   = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  rest_api_id   = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  
}

resource "aws_api_gateway_integration" "CSR_mysql_API_2_api-keys-read-write_integration_get-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_2_api-keys-read-write_get-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-keys-read-and-write-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_integration" "CSR_mysql_API_2_api-keys-read-write_integration_post-tf" {
  rest_api_id             = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  resource_id             = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  http_method             = aws_api_gateway_method.CSR_mysql_API_2_api-keys-read-write_post-tf.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  #uri                     = aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.invoke_arn
  uri                     = aws_lambda_alias.CSR-api-keys-read-and-write-api-gateway-lambda-tf.invoke_arn
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_2_api-keys-read-write_200_response_get-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_2_api-keys-read-write_get-tf.http_method
  status_code = "200"
  
}

resource "aws_api_gateway_method_response" "CSR_mysql_API_2_api-keys-read-write_200_response_post-tf" {
  rest_api_id = aws_api_gateway_rest_api.CSR_mysql_API_2-tf.id
  resource_id = aws_api_gateway_resource.CSR_mysql_API_2_api-keys-read-write-tf.id
  http_method = aws_api_gateway_method.CSR_mysql_API_2_api-keys-read-write_post-tf.http_method
  status_code = "200"
}

###########################################################
### CSR_mysql_API_2 - api-keys-read-write resource ends ###
###########################################################

###############################################
### CSR_mysql_API_2-tf - api gateway - ends ###
###############################################
