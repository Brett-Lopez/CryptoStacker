##########################################################
############### CONFIGURE CONCURRENCY ####################
##########################################################
variable "min_capacity_provisioned_concurrent_executions" {
  description = "min_capacity of provisioned_concurrent_executions"
  type        = string
  default     = "1" #prod 10
}
variable "max_capacity_provisioned_concurrent_executions" {
  description = "min_capacity of provisioned_concurrent_executions"
  type        = string
  default     = "350"
}
variable "autoscaling_target_provisioned_concurrent_executions" {
  description = "min_capacity of provisioned_concurrent_executions"
  type        = number
  default     = 0.5
}



##########################################################
##################### API GATEWAYS #######################
##########################################################

#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-users-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-users-api-gateway-lambda/CSR-users-api-gateway-lambda.zip"
  function_name = "CSR-users-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    subnet_ids = module.vpc.database_subnets
  }

}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-users-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-users-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-users-api-gateway-lambda-tf.name
  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-users-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-users-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-users-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-users-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-users-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-users-api-gateway-lambda-tf" {
    name             = "CSR-users-api-gateway-lambda-tf"
    description      = "CSR-users-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-users-api-gateway-lambda-tf.arn
    function_version = var.CSR-users-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-users-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-users-api-gateway-lambda-tf:${var.CSR-users-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-users-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-users-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-users-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-users-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-users-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-users-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}

#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-dca-schedule-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-dca-schedule-api-gateway-lambda/CSR-dca-schedule-api-gateway-lambda.zip"
  function_name = "CSR-dca-schedule-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-dca-schedule-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-dca-schedule-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-dca-schedule-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-dca-schedule-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-dca-schedule-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-dca-schedule-api-gateway-lambda-tf" {
    name             = "CSR-dca-schedule-api-gateway-lambda-tf"
    description      = "CSR-dca-schedule-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-dca-schedule-api-gateway-lambda-tf.arn
    function_version = var.CSR-dca-schedule-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-dca-schedule-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-dca-schedule-api-gateway-lambda-tf:${var.CSR-dca-schedule-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-dca-schedule-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-dca-schedule-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-dca-schedule-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-dca-schedule-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-dca-schedule-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-dca-schedule-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "2"
}

#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-dca-purchase-logs-api-gateway-lambda/CSR-dca-purchase-logs-api-gateway-lambda.zip"
  function_name = "CSR-dca-purchase-logs-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-dca-purchase-logs-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-dca-purchase-logs-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-dca-purchase-logs-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {
    name             = "CSR-dca-purchase-logs-api-gateway-lambda-tf"
    description      = "CSR-dca-purchase-logs-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-dca-purchase-logs-api-gateway-lambda-tf.arn
    function_version = var.CSR-dca-purchase-logs-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-dca-purchase-logs-api-gateway-lambda-tf:${var.CSR-dca-purchase-logs-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-dca-purchase-logs-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-dca-purchase-logs-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-dca-purchase-logs-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-dca-purchase-logs-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-dca-purchase-logs-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-dca-purchase-logs-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "2"
}

#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-delete-user-everywhere-api-gateway-lambda/CSR-delete-user-everywhere-api-gateway-lambda.zip"
  function_name = "CSR-delete-user-everywhere-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-delete-user-everywhere-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-delete-user-everywhere-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-delete-user-everywhere-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {
    name             = "CSR-delete-user-everywhere-api-gateway-lambda-tf"
    description      = "CSR-delete-user-everywhere-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-delete-user-everywhere-api-gateway-lambda-tf.arn
    function_version = var.CSR-delete-user-everywhere-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-delete-user-everywhere-api-gateway-lambda-tf:${var.CSR-delete-user-everywhere-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-delete-user-everywhere-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-delete-user-everywhere-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-delete-user-everywhere-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-delete-user-everywhere-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-delete-user-everywhere-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-delete-user-everywhere-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-pending-payments-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-pending-payments-api-gateway-lambda/CSR-pending-payments-api-gateway-lambda.zip"
  function_name = "CSR-pending-payments-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-pending-payments-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-pending-payments-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-pending-payments-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-pending-payments-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-pending-payments-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-pending-payments-api-gateway-lambda-tf" {
    name             = "CSR-pending-payments-api-gateway-lambda-tf"
    description      = "CSR-pending-payments-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-pending-payments-api-gateway-lambda-tf.arn
    function_version = var.CSR-pending-payments-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-pending-payments-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-pending-payments-api-gateway-lambda-tf:${var.CSR-pending-payments-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-pending-payments-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-pending-payments-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-pending-payments-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-pending-payments-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-pending-payments-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-pending-payments-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}

#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-subscription_tier-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-subscription-tier-api-gateway-lambda/CSR-subscription-tier-api-gateway-lambda.zip"
  function_name = "CSR-subscription_tier-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }

}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-subscription_tier-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-subscription_tier-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-subscription_tier-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-subscription_tier-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-subscription_tier-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-subscription_tier-api-gateway-lambda-tf" {
    name             = "CSR-subscription_tier-api-gateway-lambda-tf"
    description      = "CSR-subscription_tier-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-subscription_tier-api-gateway-lambda-tf.arn
    function_version = var.CSR-subscription_tier-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-subscription_tier-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-subscription_tier-api-gateway-lambda-tf:${var.CSR-subscription_tier-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-subscription_tier-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-subscription_tier-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-subscription_tier-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-subscription_tier-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-subscription_tier-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-subscription_tier-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}

#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-pricing_tier-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-pricing-tier-api-gateway-lambda/CSR-pricing-tier-api-gateway-lambda.zip"
  function_name = "CSR-pricing_tier-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-pricing_tier-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-pricing_tier-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-pricing_tier-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-pricing_tier-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-pricing_tier-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-pricing_tier-api-gateway-lambda-tf" {
    name             = "CSR-pricing_tier-api-gateway-lambda-tf"
    description      = "CSR-pricing_tier-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-pricing_tier-api-gateway-lambda-tf.arn
    function_version = var.CSR-pricing_tier-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-pricing_tier-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-pricing_tier-api-gateway-lambda-tf:${var.CSR-pricing_tier-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-pricing_tier-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-pricing_tier-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-pricing_tier-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-pricing_tier-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-pricing_tier-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-pricing_tier-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-user_subscription_status-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-user-subscription-status-api-gateway-lambda/CSR-user-subscription-status-api-gateway-lambda.zip"
  function_name = "CSR-user_subscription_status-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-user_subscription_status-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-user_subscription_status-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-user_subscription_status-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-user_subscription_status-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-user_subscription_status-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-user_subscription_status-api-gateway-lambda-tf" {
    name             = "CSR-user_subscription_status-api-gateway-lambda-tf"
    description      = "CSR-user_subscription_status-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-user_subscription_status-api-gateway-lambda-tf.arn
    function_version = var.CSR-user_subscription_status-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-user_subscription_status-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-user_subscription_status-api-gateway-lambda-tf:${var.CSR-user_subscription_status-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-user_subscription_status-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-user_subscription_status-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-user_subscription_status-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-user_subscription_status-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-user_subscription_status-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-user_subscription_status-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-user_payments-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-user-payments-api-gateway-lambda/CSR-user-payments-api-gateway-lambda.zip"
  function_name = "CSR-user_payments-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-user_payments-api-gateway-lambda-tf_perm" {
  statement_id  = "Allow-lambda-APIInvoke-tf"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-user_payments-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-user_payments-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-user_payments-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-user_payments-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-user_payments-api-gateway-lambda-tf" {
    name             = "CSR-user_payments-api-gateway-lambda-tf"
    description      = "CSR-user_payments-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-user_payments-api-gateway-lambda-tf.arn
    function_version = var.CSR-user_payments-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-user_payments-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-user_payments-api-gateway-lambda-tf:${var.CSR-user_payments-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-user_payments-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-user_payments-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-user_payments-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-user_payments-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-user_payments-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-user_payments-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "4"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-api-keys-write-only-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-api-keys-write-only-api-gateway-lambda/CSR-api-keys-write-only-api-gateway-lambda.zip"
  function_name = "CSR-api-keys-write-only-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-api-keys-write-only-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-api-keys-write-only-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-api-keys-write-only-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-api-keys-write-only-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-api-keys-write-only-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-api-keys-write-only-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-api-keys-write-only-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-api-keys-write-only-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-api-keys-write-only-api-gateway-lambda-tf" {
    name             = "CSR-api-keys-write-only-api-gateway-lambda-tf"
    description      = "CSR-api-keys-write-only-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-api-keys-write-only-api-gateway-lambda-tf.arn
    function_version = var.CSR-api-keys-write-only-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-api-keys-write-only-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-api-keys-write-only-api-gateway-lambda-tf:${var.CSR-api-keys-write-only-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-api-keys-write-only-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-api-keys-write-only-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-api-keys-write-only-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-api-keys-write-only-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-api-keys-write-only-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-api-keys-write-only-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-api-keys-read-and-write-api-gateway-lambda/CSR-api-keys-read-and-write-api-gateway-lambda.zip"
  function_name = "CSR-api-keys-read-and-write-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-api-keys-read-and-write-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-api-keys-read-and-write-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-api-keys-read-and-write-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  #source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_2-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {
    name             = "CSR-api-keys-read-and-write-api-gateway-lambda-tf"
    description      = "CSR-api-keys-read-and-write-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-api-keys-read-and-write-api-gateway-lambda-tf.arn
    function_version = var.CSR-api-keys-read-and-write-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-api-keys-read-and-write-api-gateway-lambda-tf:${var.CSR-api-keys-read-and-write-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-api-keys-read-and-write-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-api-keys-read-and-write-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-api-keys-read-and-write-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-api-keys-read-and-write-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-api-keys-read-and-write-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-api-keys-read-and-write-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS



#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-api-keys-metadata-api-gateway-lambda/CSR-api-keys-metadata-api-gateway-lambda.zip"
  function_name = "CSR-api-keys-metadata-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-api-keys-metadata-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-api-keys-metadata-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-api-keys-metadata-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-api-keys-metadata-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
    name             = "CSR-api-keys-metadata-api-gateway-lambda-tf"
    description      = "CSR-api-keys-metadata-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-api-keys-metadata-api-gateway-lambda-tf.arn
    function_version = var.CSR-api-keys-metadata-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-api-keys-metadata-api-gateway-lambda-tf:${var.CSR-api-keys-metadata-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-api-keys-metadata-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-api-keys-metadata-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-api-keys-metadata-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-api-keys-metadata-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-api-keys-metadata-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-api-keys-metadata-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-brand-ambassador-referral-codes-api-gateway-lambda/CSR-brand-ambassador-referral-codes-api-gateway-lambda.zip"
  function_name = "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {
    name             = "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf"
    description      = "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.arn
    function_version = var.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf:${var.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-brand-ambassador-referral-codes-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-failed-dca-counter-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-failed-dca-counter-api-gateway-lambda/CSR-failed-dca-counter-api-gateway-lambda.zip"
  function_name = "CSR-failed-dca-counter-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-failed-dca-counter-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-failed-dca-counter-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-failed-dca-counter-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-failed-dca-counter-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-failed-dca-counter-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-failed-dca-counter-api-gateway-lambda-tf" {
    name             = "CSR-failed-dca-counter-api-gateway-lambda-tf"
    description      = "CSR-failed-dca-counter-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-failed-dca-counter-api-gateway-lambda-tf.arn
    function_version = var.CSR-failed-dca-counter-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-failed-dca-counter-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-failed-dca-counter-api-gateway-lambda-tf:${var.CSR-failed-dca-counter-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-failed-dca-counter-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-failed-dca-counter-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-failed-dca-counter-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-failed-dca-counter-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-failed-dca-counter-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-failed-dca-counter-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-auth0-token-response-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-auth0-token-response-api-gateway-lambda/CSR-auth0-token-response-api-gateway-lambda.zip"
  function_name = "CSR-auth0-token-response-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-auth0-token-response-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-auth0-token-response-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-auth0-token-response-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-auth0-token-response-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-auth0-token-response-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-auth0-token-response-api-gateway-lambda-tf" {
    name             = "CSR-auth0-token-response-api-gateway-lambda-tf"
    description      = "CSR-auth0-token-response-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-auth0-token-response-api-gateway-lambda-tf.arn
    function_version = var.CSR-auth0-token-response-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-auth0-token-response-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-auth0-token-response-api-gateway-lambda-tf:${var.CSR-auth0-token-response-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-auth0-token-response-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-auth0-token-response-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-auth0-token-response-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-auth0-token-response-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-auth0-token-response-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-auth0-token-response-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-auth0-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-auth0-api-gateway-lambda/CSR-auth0-api-gateway-lambda.zip"
  function_name = "CSR-auth0-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-auth0-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-auth0-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier     = aws_lambda_alias.CSR-auth0-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-auth0-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-auth0-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-auth0-api-gateway-lambda-tf" {
    name             = "CSR-auth0-api-gateway-lambda-tf"
    description      = "CSR-auth0-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-auth0-api-gateway-lambda-tf.arn
    function_version = var.CSR-auth0-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-auth0-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-auth0-api-gateway-lambda-tf:${var.CSR-auth0-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-auth0-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-auth0-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-auth0-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-auth0-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-auth0-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-auth0-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "3"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-opennode-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-opennode-api-gateway-lambda/CSR-opennode-api-gateway-lambda.zip"
  function_name = "CSR-opennode-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-opennode-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-opennode-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-opennode-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-opennode-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-opennode-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-opennode-api-gateway-lambda-tf" {
    name             = "CSR-opennode-api-gateway-lambda-tf"
    description      = "CSR-opennode-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-opennode-api-gateway-lambda-tf.arn
    function_version = var.CSR-opennode-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-opennode-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-opennode-api-gateway-lambda-tf:${var.CSR-opennode-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-opennode-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-opennode-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-opennode-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-opennode-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-opennode-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-opennode-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "2"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-api-key-submission-counter-api-gateway-lambda/CSR-api-key-submission-counter-api-gateway-lambda.zip"
  function_name = "CSR-api-key-submission-counter-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-api-key-submission-counter-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-api-key-submission-counter-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-api-key-submission-counter-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {
    name             = "CSR-api-key-submission-counter-api-gateway-lambda-tf"
    description      = "CSR-api-key-submission-counter-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-api-key-submission-counter-api-gateway-lambda-tf.arn
    function_version = var.CSR-api-key-submission-counter-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-api-key-submission-counter-api-gateway-lambda-tf:${var.CSR-api-key-submission-counter-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-api-key-submission-counter-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-api-key-submission-counter-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-api-key-submission-counter-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-api-key-submission-counter-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-api-key-submission-counter-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-api-key-submission-counter-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-resend-verification-email-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-resend-verification-email-api-gateway-lambda/CSR-resend-verification-email-api-gateway-lambda.zip"
  function_name = "CSR-resend-verification-email-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-resend-verification-email-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-resend-verification-email-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-resend-verification-email-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-resend-verification-email-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-resend-verification-email-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-resend-verification-email-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-resend-verification-email-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-resend-verification-email-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-resend-verification-email-api-gateway-lambda-tf" {
    name             = "CSR-resend-verification-email-api-gateway-lambda-tf"
    description      = "CSR-resend-verification-email-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-resend-verification-email-api-gateway-lambda-tf.arn
    function_version = var.CSR-resend-verification-email-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-resend-verification-email-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-resend-verification-email-api-gateway-lambda-tf:${var.CSR-resend-verification-email-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-resend-verification-email-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-resend-verification-email-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-resend-verification-email-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-resend-verification-email-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-resend-verification-email-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-resend-verification-email-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-daily-user-metrics-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-daily-user-metrics-api-gateway-lambda/CSR-daily-user-metrics-api-gateway-lambda.zip"
  function_name = "CSR-daily-user-metrics-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-daily-user-metrics-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-daily-user-metrics-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-daily-user-metrics-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-daily-user-metrics-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-daily-user-metrics-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-daily-user-metrics-api-gateway-lambda-tf" {
    name             = "CSR-daily-user-metrics-api-gateway-lambda-tf"
    description      = "CSR-daily-user-metrics-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-daily-user-metrics-api-gateway-lambda-tf.arn
    function_version = var.CSR-daily-user-metrics-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-daily-user-metrics-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-daily-user-metrics-api-gateway-lambda-tf:${var.CSR-daily-user-metrics-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-daily-user-metrics-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-daily-user-metrics-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-daily-user-metrics-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-daily-user-metrics-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-daily-user-metrics-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-daily-user-metrics-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "2"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-daily-revenue-metrics-api-gateway-lambda/CSR-daily-revenue-metrics-api-gateway-lambda.zip"
  function_name = "CSR-daily-revenue-metrics-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-daily-revenue-metrics-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-daily-revenue-metrics-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-daily-revenue-metrics-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {
    name             = "CSR-daily-revenue-metrics-api-gateway-lambda-tf"
    description      = "CSR-daily-revenue-metrics-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-daily-revenue-metrics-api-gateway-lambda-tf.arn
    function_version = var.CSR-daily-revenue-metrics-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-daily-revenue-metrics-api-gateway-lambda-tf:${var.CSR-daily-revenue-metrics-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-daily-revenue-metrics-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-daily-revenue-metrics-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-daily-revenue-metrics-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-daily-revenue-metrics-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-daily-revenue-metrics-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-daily-revenue-metrics-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "1"
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-refresh-kyc-verification-status-api-gateway-lambda/CSR-refresh-kyc-verification-status-api-gateway-lambda.zip"
  function_name = "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = true
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#give api gateway access to lambda
resource "aws_lambda_permission" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf_perm" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf"
  principal     = "apigateway.amazonaws.com"
  qualifier = aws_lambda_alias.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.name

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.CSR_mysql_API_1-tf.execution_arn}/*/*/*"
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.function_name}"
  retention_in_days = 3
}
#provisioned concurrency
resource "aws_lambda_provisioned_concurrency_config" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {
    function_name                     = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.function_name
    provisioned_concurrent_executions = var.min_capacity_provisioned_concurrent_executions
    qualifier                         = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.version
}
resource "aws_lambda_alias" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {
    name             = "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf"
    description      = "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf"
    function_name    = aws_lambda_function.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.arn
    function_version = var.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf_provisioned_version_number
}
#auto scaling:
resource "aws_appautoscaling_target" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {
  max_capacity       = tonumber(var.max_capacity_provisioned_concurrent_executions)
  min_capacity       = tonumber(var.min_capacity_provisioned_concurrent_executions)
  resource_id        = "function:CSR-refresh-kyc-verification-status-api-gateway-lambda-tf:${var.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf_provisioned_version_number}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}
resource "aws_appautoscaling_policy" "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf" {
  name               = "LambdaProvisionedConcurrencyUtilization:${aws_appautoscaling_target.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.CSR-refresh-kyc-verification-status-api-gateway-lambda-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = var.autoscaling_target_provisioned_concurrent_executions
  }
}
#version:
variable "CSR-refresh-kyc-verification-status-api-gateway-lambda-tf_provisioned_version_number" {
  description = "lambda version to use for alias/api gateway"
  type        = string
  default     = "3"
}
#CREATE LAMBDA BLOCK ENDS


##############################################
##############################################
############## DCA PURCHASER #################
##############################################
##############################################


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-dca-purchaser-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-dca-purchaser/CSR-dca-purchaser.zip"
  function_name = "CSR-dca-purchaser-lambda-tf"
  role          = aws_iam_role.CSR-dca-purchaser-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 100
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#lambda event_source_mapping
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping
resource "aws_lambda_event_source_mapping" "CSR-dca-purchaser-lambda-tf" {
  event_source_arn = aws_sqs_queue.CRS-cron-events-dca-tf.arn
  function_name    = aws_lambda_function.CSR-dca-purchaser-lambda-tf.arn
  batch_size = 1
  maximum_batching_window_in_seconds = 5
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-dca-purchaser-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-dca-purchaser-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


##############################################
##############################################
############## batch jobs ####################
##############################################
##############################################


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-mysql-create-dbs-and-tables-1-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-mysql-create-dbs-and-tables-1-lambda/CSR-mysql-create-dbs-and-tables-1-lambda.zip" 
  function_name = "CSR-mysql-create-dbs-and-tables-1-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn 
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-mysql-create-dbs-and-tables-1-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-mysql-create-dbs-and-tables-1-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-mysql-fill-tables-1-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-mysql-fill-tables-1-lambda/CSR-mysql-fill-tables-1-lambda.zip"
  function_name = "CSR-mysql-fill-tables-1-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-mysql-fill-tables-1-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-mysql-fill-tables-1-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS



#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-mysql-create-dbs-and-tables-2-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-mysql-create-dbs-and-tables-2-lambda/CSR-mysql-create-dbs-and-tables-2-lambda.zip"
  function_name = "CSR-mysql-create-dbs-and-tables-2-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-mysql-create-dbs-and-tables-2-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-mysql-create-dbs-and-tables-2-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-mysql-fill-tables-2-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-mysql-fill-tables-2-lambda/CSR-mysql-fill-tables-2-lambda.zip" 
  function_name = "CSR-mysql-fill-tables-2-lambda-tf"
  role          = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn 
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = -1
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 60
  vpc_config {
    security_group_ids = [aws_security_group.api-gateway-lambda-tf.id]
    
    subnet_ids = module.vpc.database_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-mysql-fill-tables-2-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-mysql-fill-tables-2-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS



#CREATE LAMBDA BLOCK STARTS
#cron events btc
resource "aws_lambda_function" "CSR-cron-events-btc-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-cron-events-btc/cron-events-btc-deployment-package.zip" 
  function_name = "CSR-cron-events-btc-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }

}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-cron-events-btc-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-cron-events-btc-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
#cron events ltc
resource "aws_lambda_function" "CSR-cron-events-ltc-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-cron-events-ltc/cron-events-ltc-deployment-package.zip" 
  function_name = "CSR-cron-events-ltc-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-cron-events-ltc-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-cron-events-ltc-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
#cron events eth
resource "aws_lambda_function" "CSR-cron-events-eth-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-cron-events-eth/cron-events-eth-deployment-package.zip" 
  function_name = "CSR-cron-events-eth-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-cron-events-eth-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-cron-events-eth-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-delete-pending-payments-old-ddos-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-delete-pending-payments-old-ddos-lambda/CSR-delete-pending-payments-old-ddos-lambda.zip"
  function_name = "CSR-delete-pending-payments-old-ddos-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-delete-pending-payments-old-ddos-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-delete-pending-payments-old-ddos-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-pending-to-payments-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-pending-to-payments-lambda/CSR-pending-to-payments-lambda.zip"
  function_name = "CSR-pending-to-payments-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-pending-to-payments-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-pending-to-payments-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-delete-redis-keys-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-delete-redis-keys-lambda/CSR-delete-redis-keys.zip"
  function_name = "CSR-delete-redis-keys-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn 
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-delete-redis-keys-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-delete-redis-keys-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-warm-all-services-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-warm-all-services-lambda/CSR-warm-all-services.zip"
  function_name = "CSR-warm-all-services-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn 
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-warm-all-services-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-warm-all-services-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-reschedule-missed-dca-schedules-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-reschedule-missed-dca-schedules-lambda/CSR-reschedule-missed-dca-schedules-lambda.zip"
  function_name = "CSR-reschedule-missed-dca-schedules-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-reschedule-missed-dca-schedules-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-reschedule-missed-dca-schedules-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS



#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-reset-hourly-api-key-counter-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-reset-hourly-api-key-counter-lambda/CSR-reset-hourly-api-key-counter-lambda.zip"
  function_name = "CSR-reset-hourly-api-key-counter-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-reset-hourly-api-key-counter-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-reset-hourly-api-key-counter-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-reset-monthly-subscription-counters-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-reset-monthly-subscription-counters-lambda/CSR-reset-monthly-subscription-counters-lambda.zip"
  function_name = "CSR-reset-monthly-subscription-counters-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-reset-monthly-subscription-counters-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-reset-monthly-subscription-counters-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-delete-expired-api-keys-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-delete-expired-api-keys-lambda/CSR-delete-expired-api-keys-lambda.zip"
  function_name = "CSR-delete-expired-api-keys-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-delete-expired-api-keys-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-delete-expired-api-keys-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-update-persona-validation-status-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-update-persona-validation-status-lambda/CSR-update-persona-validation-status-lambda.zip"
  function_name = "CSR-update-persona-validation-status-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 20
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-update-persona-validation-status-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-update-persona-validation-status-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-create-daily-metrics-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-create-daily-metrics-lambda/CSR-create-daily-metrics-lambda.zip"
  function_name = "CSR-create-daily-metrics-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-create-daily-metrics-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-create-daily-metrics-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-create-daily-revenue-metrics-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-create-daily-revenue-metrics-lambda/CSR-create-daily-revenue-metrics-lambda.zip"
  function_name = "CSR-create-daily-revenue-metrics-lambda-tf"
  role          = aws_iam_role.CSR-cron-events-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-create-daily-revenue-metrics-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-create-daily-revenue-metrics-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS


#CREATE LAMBDA BLOCK STARTS
resource "aws_lambda_function" "CSR-refresh-ecs-tasks-lambda-tf" {
  filename      = "/home/brett/Desktop/lambda/CSR-refresh-ecs-tasks-lambda/CSR-refresh-ecs-tasks-lambda.zip"
  function_name = "CSR-refresh-ecs-tasks-lambda-tf"
  role          = aws_iam_role.CSR-ecs-fargate-tasks-lambda-tf.arn
  handler       = "lambda_function.lambda_handler"
  architectures = ["x86_64"]
  kms_key_arn = aws_kms_key.CSR-lambda-env-var-tf.arn
  memory_size = 256
  #package_type = #
  reserved_concurrent_executions = 5
  publish = false #(Optional) Whether to publish creation/change as new Lambda Function Version. Defaults to false.
  runtime = "python3.9"
  timeout = 900
  vpc_config {
    security_group_ids = [aws_security_group.allow_from_private_subnets-tf.id]
    
    subnet_ids = module.vpc.private_subnets
  }
}

#set cloudwatch logs retention
resource "aws_cloudwatch_log_group" "CSR-refresh-ecs-tasks-lambda-tf" {  
  name = "/aws/lambda/${aws_lambda_function.CSR-refresh-ecs-tasks-lambda-tf.function_name}"
  retention_in_days = 3
}
#CREATE LAMBDA BLOCK ENDS



