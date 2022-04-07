resource "aws_elasticache_replication_group" "CSR-flask-session-redis-tf" {
  automatic_failover_enabled    = true
  multi_az_enabled              = true
  availability_zones            = ["${var.AWS_REGION}a", "${var.AWS_REGION}b", "${var.AWS_REGION}c"]
  replication_group_id          = "CSR-redis-flask-session-tf"
  replication_group_description = "This redis DB is used by flask-session"
  node_type                     = "cache.t2.micro" 
  
  number_cache_clusters         = 3
  engine                        = "redis"
  engine_version                = "6.x"
  parameter_group_name          = "default.redis6.x"
  port                          = 6379
  apply_immediately = true
  security_group_ids = [aws_security_group.allow_all_internal_subnets-tf.id]
  subnet_group_name = aws_elasticache_subnet_group.CSR-flask-session-redis-tf.name
  at_rest_encryption_enabled = true
  
  kms_key_id = aws_kms_key.CSR-redis-at-rest-encryption-tf.arn
}


resource "aws_elasticache_subnet_group" "CSR-flask-session-redis-tf" {
  name       = "CSR-flask-session-redis-cache-subnet-tf"
  subnet_ids = module.vpc.elasticache_subnets
}
