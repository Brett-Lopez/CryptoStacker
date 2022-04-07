
#CREATE SECURITY GROUP MODULE - https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
module "allow_from_home_ip_tcp" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "allow_from_home_ip_tcp-tf"
  description = "allow all traffic from home IP address"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks      = ["71.227.211.17/32"]
  ingress_rules            = ["https-443-tcp"]
  ingress_with_cidr_blocks = [
    {
      from_port   = 8080
      to_port     = 8090
      protocol    = "tcp"
      description = "User-service ports"
      cidr_blocks = "71.227.211.17/32"
    },
    {
      rule        = "postgresql-tcp"
      cidr_blocks = "71.227.211.17/32"
    },
  ]
}

#create security groups
module "allow_nothing" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "allow_nothing-tf"
  description = "allow nothing"
  vpc_id      = module.vpc.vpc_id
}

#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_all_from_home-tf" {
  name        = "allow_all_from_home-tf"
  description = "Allow all inbound from home traffic"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_from_home_inbound" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["71.227.211.17/32", "50.35.110.106/32"]
  security_group_id = aws_security_group.allow_all_from_home-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_from_home_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_all_from_home-tf.id
}

#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_ssh_from_home-tf" {
  name        = "allow_ssh_from_home-tf"
  description = "Allow SSH inbound from home traffic"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description      = "SSH over TCP"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["71.227.211.17/32", "50.35.110.106/32"]
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}


#################################
### ALB & ECS security groups ###
#################################

#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_all_for_alb-tf" {
  name        = "allow_all_for_alb-tf"
  description = "Allow all inbound & outbound traffic for the ALB, IPs can be restricted with WAF instead"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_for_alb_inbound" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_all_for_alb-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_for_alb_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_all_for_alb-tf.id
}


#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_ecs_sg-tf" {
  name        = "allow_ecs_sg-tf"
  description = "Allow traffic to/from containers in ECS security group"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_ecs_sg_inbound" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  source_security_group_id = aws_security_group.allow_all_for_alb-tf.id
  security_group_id = aws_security_group.allow_ecs_sg-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_ecs_sg_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_ecs_sg-tf.id
}
######################################
### ALB & ECS security groups ends ###
######################################




#api-gateway-lambda 
#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "api-gateway-lambda-tf" {
  name        = "api-gateway-lambda-tf"
  description = "Allow traffic required for API gateway lambdas"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_outbound_api-gateway-lambda-tf" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.api-gateway-lambda-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_inbound_from_intra_subnets_api-gateway-lambda-tf" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  #cidr_blocks       = module.vpc.intra_subnets_cidr_blocks
  cidr_blocks       = module.vpc.database_subnets_cidr_blocks
  security_group_id = aws_security_group.api-gateway-lambda-tf.id
}

#allow_all_internal_subnets
#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_all_internal_subnets-tf" {
  name        = "allow_all_internal_subnets-tf"
  description = "Allow all traffic from internal subnets"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_outbound_allow_all_internal_subnets-tf" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_all_internal_subnets-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_inbound_from_all_internal_subnets_allow_all_internal_subnets-tf" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = concat(module.vpc.public_subnets_cidr_blocks, module.vpc.database_subnets_cidr_blocks, module.vpc.private_subnets_cidr_blocks, module.vpc.intra_subnets_cidr_blocks)
  security_group_id = aws_security_group.allow_all_internal_subnets-tf.id
}


#allow_from_private_subnets
#create security group - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "allow_from_private_subnets-tf" {
  name        = "allow_from_private_subnets-tf"
  description = "Allow all traffic from private subnets"
  vpc_id      = module.vpc.vpc_id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_all_outbound_allow_private_subnets-tf" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_from_private_subnets-tf.id
}
#create security group RULE - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
resource "aws_security_group_rule" "allow_inbound_from_private_subnets_allow_from_private_subnets-tf" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = concat(module.vpc.private_subnets_cidr_blocks)
  security_group_id = aws_security_group.allow_from_private_subnets-tf.id
}
