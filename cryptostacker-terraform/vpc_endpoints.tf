#https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html#apigateway-private-api-test-invoke-url
#https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-api-test-invoke-url.html
#https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies-examples.html#apigateway-resource-policies-source-vpc-example


resource "aws_vpc_endpoint" "api_gateway_endpoint_private_subnet-tf" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.AWS_REGION}.execute-api"
  vpc_endpoint_type = "Interface"
  subnet_ids = concat(module.vpc.private_subnets)
  security_group_ids = [
    aws_security_group.allow_all_internal_subnets-tf.id,
  ]

  private_dns_enabled = true

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": [
                "*"
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


resource "aws_vpc_endpoint" "KMS_endpoint_private_subnet-tf" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.AWS_REGION}.kms"
  vpc_endpoint_type = "Interface"
  subnet_ids = concat(module.vpc.private_subnets)
  security_group_ids = [
    aws_security_group.allow_all_internal_subnets-tf.id,
  ]

  private_dns_enabled = true

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "kms:*",
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "kms:*",
            "Resource": [
                "*"
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

resource "aws_vpc_endpoint" "secrets_manager_endpoint_private_subnet-tf" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.AWS_REGION}.secretsmanager"
  vpc_endpoint_type = "Interface"
  subnet_ids = concat(module.vpc.private_subnets)
  security_group_ids = [
    aws_security_group.allow_all_internal_subnets-tf.id,
  ]

  private_dns_enabled = true

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "secretsmanager:*",
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "secretsmanager:*",
            "Resource": [
                "*"
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
