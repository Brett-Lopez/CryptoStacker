terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.74.0"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = var.AWS_REGION
}

#CREATE VPC MODULE - https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "CSR-VPC-${var.AWS_REGION}-TF"
  cidr = "10.0.0.0/16"

  azs             = ["${var.AWS_REGION}a", "${var.AWS_REGION}b", "${var.AWS_REGION}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.51.0/24", "10.0.52.0/24", "10.0.53.0/24"]
  intra_subnets = ["10.0.61.0/24", "10.0.62.0/24", "10.0.63.0/24"] #no internet access subnets
  elasticache_subnets = ["10.0.71.0/24", "10.0.72.0/24", "10.0.73.0/24"]

  enable_nat_gateway = true

  single_nat_gateway = false 
  one_nat_gateway_per_az = true

  enable_vpn_gateway = false
  enable_dns_hostnames = true #required for vpc private endpoints
  enable_dns_support   = true #required for vpc private endpoints

}
