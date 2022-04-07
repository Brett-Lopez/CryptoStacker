#CSR-EC2-PROTO-BROAD-ROLE-TF
#CSR-EC2-PROD-NARROW-ROLE-TF
#CREATE IAM ROLE FOR EC2s - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
resource "aws_iam_role" "CSR-EC2-PROTO-BROAD-ROLE-TF" {
  name = "CSR-EC2-PROTO-BROAD-ROLE-TF"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

#CREATE IAM ROLE FOR LAMBDAS - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
resource "aws_iam_role" "CSR-LAMBDA-PROTO-BROAD-ROLE-TF" {
  name = "CSR-LAMBDA-PROTO-BROAD-ROLE-TF"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


#CREATE IAM ROLE FOR LAMBDAS - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#CSR-API-GATEWAY-LAMBDAS-1-TF
resource "aws_iam_role" "CSR-API-GATEWAY-LAMBDAS-1-TF" {
  name = "CSR-API-GATEWAY-LAMBDAS-1-TF"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

#CREATE IAM ROLE FOR LAMBDAS - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#CSR-API-GATEWAY-LAMBDAS-2-TF
resource "aws_iam_role" "CSR-API-GATEWAY-LAMBDAS-2-TF" {
  name = "CSR-API-GATEWAY-LAMBDAS-2-TF"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


##################################################
### CSR-ECS-TASKS-WWW-WEBAPP-TF SECTION BEGINS ###
##################################################

#CREATE IAM ROLE FOR ECS containers/tasks - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#https://stackoverflow.com/questions/55643095/what-is-the-difference-between-ecs-amazonaws-com-and-ecs-tasks-amazonaws-com
resource "aws_iam_role" "CSR-ECS-TASKS-WWW-WEBAPP-TF" {
  name = "CSR-ECS-TASKS-WWW-WEBAPP-TF"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

#CSR-ECS-TASKS-WWW-WEBAPP-TF_AmazonECSTaskExecutionRolePolicy
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-ECS-TASKS-WWW-WEBAPP-TF_AmazonECSTaskExecutionRolePolicy" {
  role       = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


#define iam policy for CSR-ECS-TASKS-WWW-WEBAPP-TF secrets manager secret
resource "aws_iam_policy" "CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only" {
  name        = "CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only"
  path        = "/"
  description = "CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
             "Resource": [
                "${aws_secretsmanager_secret.CSR-auth0-api-keys-tf.arn}",
                "${aws_secretsmanager_secret.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.arn}",
                "${aws_secretsmanager_secret.CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF.arn}",
                "${aws_secretsmanager_secret.CSR-Service-Mesh-Secret_1-TF.arn}"
              ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}


##ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-ECS-TASKS-WWW-WEBAPP-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only" {
  role       = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.name
  policy_arn = aws_iam_policy.CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE - CSR-auth0-api-keys-tf
resource "aws_kms_grant" "CSR-auth0-api-keys-tf_CSR-ECS-TASKS-WWW-WEBAPP-TF" {
  name              = "CSR-auth0-api-keys-tf_CSR-ECS-TASKS-WWW-WEBAPP-TF"
  key_id            = aws_kms_key.CSR-auth0-api-keys-tf.key_id
  grantee_principal = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - REDIS
resource "aws_kms_grant" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF" {
  name              = "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF"
  key_id            = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.key_id
  grantee_principal = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - app_secret
resource "aws_kms_grant" "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF" {
  name              = "CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF"
  key_id            = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF.key_id
  grantee_principal = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - Service-Mesh
resource "aws_kms_grant" "CSR-Service-Mesh-Secret_1-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF" {
  name              = "CSR-Service-Mesh-Secret_1-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
  grantee_principal = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}

##################################################
#### CSR-ECS-TASKS-WWW-WEBAPP-TF SECTION ENDS ####
##################################################


########################################
# CSR-auth0-api-keys-2-tf begins
########################################

resource "aws_iam_policy" "CSR-auth0-api-keys-2-tf_read_only" {
  name        = "CSR-auth0-api-keys-2-tf_read_only"
  path        = "/"
  description = "CSR-auth0-api-keys-2-tf_read_only"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
             "Resource": [
                "${aws_secretsmanager_secret.CSR-auth0-api-keys-2-tf.arn}"
              ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}

##ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-auth0-api-keys-2-tf_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-auth0-api-keys-2-tf_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE - CSR-auth0-api-keys-tf
resource "aws_kms_grant" "CSR-auth0-api-keys-2-tf_CSR-auth0-api-keys-2-tf_read_only" {
  name              = "CSR-auth0-api-keys-2-tf_CSR-auth0-api-keys-2-tf_read_only"
  key_id            = aws_kms_key.CSR-auth0-api-keys-2-tf.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}

########################################
# CSR-auth0-api-keys-2-tf ends
########################################



#define policies

#define iam policy for CSR-ecs-fargate-tasks lambdas
resource "aws_iam_policy" "CSR-ecs-fargate-tasks_ephemeral-tf" {
  name        = "CSR-ecs-fargate-tasks_ephemeral-tf"
  path        = "/"
  description = "CSR-ecs-fargate-tasks_ephemeral-tf"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecs:DescribeServices",
                "ecs:DescribeCapacityProviders",
                "ecs:DescribeClusters",
                "ecs:DescribeContainerInstances",
                "ecs:DescribeTaskDefinition",
                "ecs:DescribeTasks",
                "ecs:DescribeTaskSets",
                "ecs:ListClusters",
                "ecs:ListContainerInstances",
                "ecs:ListServices",
                "ecs:ListTaskDefinitions",
                "ecs:ListTaskDefinitionFamilies",
                "ecs:ListTasks",
                "ecs:UpdateService"
                #"ecs:xxx",
                #"ecs:xxx",
                #"ecs:xxx"
            ],
            "Resource": [
              "${aws_ecs_cluster.csr-flask-web-app-ecs-cluster-tf.arn}",
              "${aws_ecs_service.csr-flask-web-app-service-tf.id}"
              ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}



#define iam policy for CSR-Service-Mesh-Secret_1 secrets manager secret
resource "aws_iam_policy" "CSR-Service-Mesh-Secret_1_sm_read_only" {
  name        = "CSR-Service-Mesh-Secret_1_sm_read_only"
  path        = "/"
  description = "CSR-Service-Mesh-Secret_1_secrets_manager_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-Service-Mesh-Secret_1-TF.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}

#define iam policy for CSR-opennode_api_key-TF secrets manager secret
resource "aws_iam_policy" "CSR-opennode_api_key-TF_read_only" {
  name        = "CSR-opennode_api_key-TF_read_only"
  path        = "/"
  description = "CSR-opennode_api_key-TF_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-opennode_api_key-TF.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}


#define iam policy for CSR-sendgrid_api_key-TF secrets manager secret
resource "aws_iam_policy" "CSR-sendgrid_api_key-TF_read_only" {
  name        = "CSR-sendgrid_api_key-TF_read_only"
  path        = "/"
  description = "CSR-sendgrid_api_key-TF_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-sendgrid_api_key-TF.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}



#define iam policy for CSR-persona-secrets-TF secrets manager secret
resource "aws_iam_policy" "CSR-persona-secrets-TF_read_only" {
  name        = "CSR-persona-secrets-TF_read_only"
  path        = "/"
  description = "CSR-persona-secrets-TF_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-persona-secrets-TF.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}


#####################################################
### CSR-cron-events-lambda-tf SECTION BEGINS ########
#####################################################

#CREATE IAM ROLE FOR CRON LAMBDAS - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#https://stackoverflow.com/questions/55643095/what-is-the-difference-between-ecs-amazonaws-com-and-ecs-tasks-amazonaws-com
resource "aws_iam_role" "CSR-cron-events-lambda-tf" {
  name = "CSR-cron-events-lambda-tf"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-cron-events-lambda-tf-AWSLambdaRole" {
  role       = aws_iam_role.CSR-cron-events-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-cron-events-lambda-tf_AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.CSR-cron-events-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-cron-events-lambda-tf_CSR-Service-Mesh-Secret_1_sm_read_only" {
  role       = aws_iam_role.CSR-cron-events-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-Service-Mesh-Secret_1_sm_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-cron-events-lambda-tf_CSR-opennode_api_key-TF_read_only" {
  role       = aws_iam_role.CSR-cron-events-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-opennode_api_key-TF_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-cron-events-lambda-tf_CSR-persona-secrets-TF_read_only" {
  role       = aws_iam_role.CSR-cron-events-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-persona-secrets-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-cron-events-lambda-tf_CSR-Service-Mesh-Secret_1-TF" {
  name              = "CSR-cron-events-lambda-tf_CSR-Service-Mesh-Secret_1-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
  grantee_principal = aws_iam_role.CSR-cron-events-lambda-tf.arn
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-cron-events-lambda-tf_CRS-cron-events-dca-tf" {
  name              = "CSR-cron-events-lambda-tf_CRS-cron-events-dca-tf"
  key_id            = aws_kms_key.CRS-cron-events-dca-tf.key_id
  grantee_principal = aws_iam_role.CSR-cron-events-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  #operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - opennode api key
resource "aws_kms_grant" "CSR-opennode_api_key-TF_CSR-cron-events-lambda-tf" {
  name              = "CSR-opennode_api_key-TF_CSR-cron-events-lambda-tf"
  key_id            = aws_kms_key.CSR-opennode_api_key-TF.key_id
  grantee_principal = aws_iam_role.CSR-cron-events-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - persona api key
resource "aws_kms_grant" "CSR-persona-secrets-TF_CSR-cron-events-lambda-tf" {
  name              = "CSR-persona-secrets-TF_CSR-cron-events-lambda-tf"
  key_id            = aws_kms_key.CSR-persona-secrets-TF.key_id
  grantee_principal = aws_iam_role.CSR-cron-events-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt"]
}


#####################################################
### CSR-cron-events-lambda-tf SECTION ENDS ##########
#####################################################


#####################################################
### CSR-dca-purchaser-lambda-tf SECTION BEGINS ######
#####################################################

#CREATE IAM ROLE FOR ECS containers/tasks - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#https://stackoverflow.com/questions/55643095/what-is-the-difference-between-ecs-amazonaws-com-and-ecs-tasks-amazonaws-com
resource "aws_iam_role" "CSR-dca-purchaser-lambda-tf" {
  name = "CSR-dca-purchaser-lambda-tf"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-dca-purchaser-lambda-tf-AWSLambdaRole" {
  role       = aws_iam_role.CSR-dca-purchaser-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-dca-purchaser-lambda-tf_AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.CSR-dca-purchaser-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_1_sm_read_only" {
  role       = aws_iam_role.CSR-dca-purchaser-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-Service-Mesh-Secret_1_sm_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_2-TF_read_only" {
  role       = aws_iam_role.CSR-dca-purchaser-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-Service-Mesh-Secret_2-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_1-TF" {
  name              = "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_1-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
  grantee_principal = aws_iam_role.CSR-dca-purchaser-lambda-tf.arn
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-dca-purchaser-lambda-tf_CRS-cron-events-dca-tf" {
  name              = "CSR-dca-purchaser-lambda-tf_CRS-cron-events-dca-tf"
  key_id            = aws_kms_key.CRS-cron-events-dca-tf.key_id
  grantee_principal = aws_iam_role.CSR-dca-purchaser-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  #operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-dca-purchaser-lambda-tf_CSR-user-api-keys-backend-tf" {
  name              = "CSR-dca-purchaser-lambda-tf_CSR-user-api-keys-backend-tf"
  key_id            = aws_kms_key.CSR-user-api-keys-backend-tf.key_id
  grantee_principal = aws_iam_role.CSR-dca-purchaser-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt"]
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_2-TF" {
  name              = "CSR-dca-purchaser-lambda-tf_CSR-Service-Mesh-Secret_2-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_2-TF.key_id
  grantee_principal = aws_iam_role.CSR-dca-purchaser-lambda-tf.arn
  operations        = ["Encrypt", "Decrypt"]
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
}

#####################################################
### CSR-dca-purchaser-lambda-tf SECTION ENDS ########
#####################################################


###########################################################
### CSR-ecs-fargate-tasks-lambda-tf SECTION BEGINS ########
###########################################################

#CREATE IAM ROLE FOR CRON LAMBDAS - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
#https://stackoverflow.com/questions/55643095/what-is-the-difference-between-ecs-amazonaws-com-and-ecs-tasks-amazonaws-com
resource "aws_iam_role" "CSR-ecs-fargate-tasks-lambda-tf" {
  name = "CSR-ecs-fargate-tasks-lambda-tf"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-ecs-fargate-tasks-lambda-tf-AWSLambdaRole" {
  role       = aws_iam_role.CSR-ecs-fargate-tasks-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-ecs-fargate-tasks-lambda-tf_AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.CSR-ecs-fargate-tasks-lambda-tf.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-ecs-fargate-tasks-lambda-tf_CSR-ecs-fargate-tasks_ephemeral-tf" {
  role       = aws_iam_role.CSR-ecs-fargate-tasks-lambda-tf.name
  policy_arn = aws_iam_policy.CSR-ecs-fargate-tasks_ephemeral-tf.arn
}


###########################################################
### CSR-ecs-fargate-tasks-lambda-tf SECTION ENDS ##########
###########################################################



#define iam policy for serverless-db-1 secrets manager secret
resource "aws_iam_policy" "CSR-primary-serverless-db-1-tf_read_only" {
  name        = "CSR-primary-serverless-db-1-tf_read_only"
  path        = "/"
  description = "CSR-primary-serverless-db-1-tf_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": [
              "${aws_secretsmanager_secret.CSR-primary-serverless-db-1-tf.arn}",
              "${aws_secretsmanager_secret.CSR-opennode_api_key-TF.arn}"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}

#CSR-API-GATEWAY-LAMBDAS-1-TF section begins
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-AWSLambdaRole" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
#api gateways require auth0 secrets and redis secrets
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-primary-serverless-db-1-tf_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-primary-serverless-db-1-tf_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE - CSR-auth0-api-keys-tf
resource "aws_kms_grant" "CSR-auth0-api-keys-tf_CSR-API-GATEWAY-LAMBDAS-1-TF" {
  name              = "CSR-auth0-api-keys-tf_CSR-API-GATEWAY-LAMBDAS-1-TF"
  key_id            = aws_kms_key.CSR-auth0-api-keys-tf.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - REDIS
resource "aws_kms_grant" "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF_CSR-API-GATEWAY-LAMBDAS-1-TF" {
  name              = "CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF_CSR-API-GATEWAY-LAMBDAS-1-TF"
  key_id            = aws_kms_key.CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-primary-serverless-db-1-tf" {
  name              = "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-primary-serverless-db-1-tf"
  key_id            = aws_kms_key.CSR-primary-serverless-db-1-tf.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-Service-Mesh-Secret_1_sm_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-Service-Mesh-Secret_1_sm_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-sendgrid_api_key-TF_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-sendgrid_api_key-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-Service-Mesh-Secret_1-TF" {
  name              = "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-Service-Mesh-Secret_1-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - opennode
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-opennode_api_key-TF" {
  name              = "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-opennode_api_key-TF"
  key_id            = aws_kms_key.CSR-opennode_api_key-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE - send grid
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-sendgrid_api_key-TF" {
  name              = "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-sendgrid_api_key-TF"
  key_id            = aws_kms_key.CSR-sendgrid_api_key-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-1-TF_CSR-persona-secrets-TF_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.name
  policy_arn = aws_iam_policy.CSR-persona-secrets-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE - persona api key
resource "aws_kms_grant" "CSR-persona-secrets-TF_CSR-API-GATEWAY-LAMBDAS-1-TF" {
  name              = "CSR-persona-secrets-TF_CSR-API-GATEWAY-LAMBDAS-1-TF"
  key_id            = aws_kms_key.CSR-persona-secrets-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-1-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}


#CSR-API-GATEWAY-LAMBDAS-1-TF section ends


#define iam policy for serverless-db-2 secrets manager secret
resource "aws_iam_policy" "CSR-primary-serverless-db-2-tf_read_only" {
  name        = "CSR-primary-serverless-db-2-tf_read_only"
  path        = "/"
  description = "CSR-primary-serverless-db-2-tf_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-primary-serverless-db-2-tf.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}


#define iam policy for serverless-db-2 secrets manager secret
resource "aws_iam_policy" "CSR-Service-Mesh-Secret_2-TF_read_only" {
  name        = "CSR-Service-Mesh-Secret_2-TF_read_only"
  path        = "/"
  description = "CSR-Service-Mesh-Secret_2-TF_read_only"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "${aws_secretsmanager_secret.CSR-Service-Mesh-Secret_2-TF.arn}"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "secretsmanager:ListSecrets",
            "Resource": "*"
        }
    ]
})
}

#CSR-API-GATEWAY-LAMBDAS-2-TF section begins
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-2-AWSLambdaRole" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-2-TF_AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-primary-serverless-db-2-tf_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.name
  policy_arn = aws_iam_policy.CSR-primary-serverless-db-2-tf_read_only.arn
}
#ATTACH IAM ROLE TO IAM POLICY - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only" {
  role       = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.name
  policy_arn = aws_iam_policy.CSR-ECS-TASKS-WWW-WEBAPP-TF_read_only.arn
}
#ATTACH KMS KEY TO IAM ROLE - Service-Mesh
resource "aws_kms_grant" "CSR-Service-Mesh-Secret_1-TF_CSR-API-GATEWAY-LAMBDAS-2-TF" {
  name              = "CSR-Service-Mesh-Secret_1-TF_CSR-API-GATEWAY-LAMBDAS-2-TF"
  key_id            = aws_kms_key.CSR-Service-Mesh-Secret_1-TF.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  operations        = ["Encrypt", "Decrypt"]
}
#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-primary-serverless-db-2-tf" {
  name              = "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-primary-serverless-db-2-tf"
  key_id            = aws_kms_key.CSR-primary-serverless-db-2-tf.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  operations        = ["Encrypt", "Decrypt"]
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
}


#ATTACH KMS KEY TO IAM ROLE
resource "aws_kms_grant" "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-user-api-keys-backend-tf" {
  name              = "CSR-API-GATEWAY-LAMBDAS-2-TF_CSR-user-api-keys-backend-tf"
  key_id            = aws_kms_key.CSR-user-api-keys-backend-tf.key_id
  grantee_principal = aws_iam_role.CSR-API-GATEWAY-LAMBDAS-2-TF.arn
  operations        = ["Encrypt", "Decrypt"]
  #operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
}
#CSR-API-GATEWAY-LAMBDAS-2-TF section ends


###################################################################
#### Container builder user
###################################################################
resource "aws_iam_user" "CSR-container-image-builder-tf" {
  name = "CSR-container-image-builder"
  path = "/"

}

resource "aws_iam_user_policy" "CSR-container-image-builder-tf" {
  name = "CSR-container-image-builder-tf"
  user = aws_iam_user.CSR-container-image-builder-tf.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
          "ecr:TagResource",
          "ecr:UntagResource",
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:PutImage"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}
###################################################################
#### Container builder user - end
###################################################################

