module "primary-serverless-db-1-tf" {
  
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 5.0"

  name              = "primary-serverless-db-1-tf" 
  engine            = "aurora-mysql"
  engine_mode       = "serverless"
  storage_encrypted = true
  publicly_accessible = false 

  vpc_id                = module.vpc.vpc_id
  
  subnets = module.vpc.database_subnets

  create_security_group = true 
  
  
  allowed_cidr_blocks   = concat(module.vpc.public_subnets_cidr_blocks, module.vpc.database_subnets_cidr_blocks, module.vpc.private_subnets_cidr_blocks, module.vpc.intra_subnets_cidr_blocks) 
  
  deletion_protection = false 
  apply_immediately   = true 
  skip_final_snapshot = true 
  backup_retention_period = 1 
  preferred_backup_window = "02:00-03:00" 
  preferred_maintenance_window = "sun:05:00-sun:06:00" 
  
  username = var.primary_serverless_db_1_USERNAME_tf
  password = var.primary_serverless_db_1_PASSWORD_tf
  create_random_password = false 
  enable_http_endpoint = true 
  iam_database_authentication_enabled = false 
  replica_scale_enabled = false 
  replica_count         = 0 
  monitoring_interval = 60 
  db_parameter_group_name         = "default.aurora-mysql5.7"
  db_cluster_parameter_group_name = "default.aurora-mysql5.7"
  

  scaling_configuration = {
    auto_pause               = false 
    min_capacity             = 1 
    max_capacity             = 64 
    seconds_until_auto_pause = 600
    timeout_action           = "ForceApplyCapacityChange" 
  }
}


module "primary-serverless-db-2-tf" {
  
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 5.0"

  name              = "primary-serverless-db-2-tf" 
  engine            = "aurora-mysql"
  engine_mode       = "serverless"
  storage_encrypted = true
  publicly_accessible = false 

  vpc_id                = module.vpc.vpc_id
  
  subnets = module.vpc.database_subnets

  create_security_group = true 
  
  
  allowed_cidr_blocks   = concat(module.vpc.public_subnets_cidr_blocks, module.vpc.database_subnets_cidr_blocks, module.vpc.private_subnets_cidr_blocks, module.vpc.intra_subnets_cidr_blocks) 
  
  deletion_protection = false 
  apply_immediately   = true 
  skip_final_snapshot = true 
  backup_retention_period = 1 
  preferred_backup_window = "02:00-03:00" 
  preferred_maintenance_window = "sun:05:00-sun:06:00" 
  
  username = var.primary_serverless_db_2_USERNAME_tf 
  password = var.primary_serverless_db_2_PASSWORD_tf
  create_random_password = false 
  enable_http_endpoint = false 
  iam_database_authentication_enabled = false 
  replica_scale_enabled = false 
  replica_count         = 0 
  monitoring_interval = 60 
  db_parameter_group_name         = "default.aurora-mysql5.7"
  db_cluster_parameter_group_name = "default.aurora-mysql5.7"
  

  scaling_configuration = {
    auto_pause               = false 
    min_capacity             = 1 
    max_capacity             = 64 
    seconds_until_auto_pause = 600
    timeout_action           = "ForceApplyCapacityChange" 
  }
}
