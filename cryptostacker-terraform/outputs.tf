#outputs
output "private_subnet_arns" {
  value = module.vpc.private_subnet_arns
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "private_subnets_cidr_blocks" {
  value = module.vpc.private_subnets_cidr_blocks
}

output "security_group_id" {
  value = module.allow_from_home_ip_tcp.security_group_id
}

output "test1" {
  value = "${var.AWS_REGION}a"
}
output "test2" {
  value = "${var.AWS_REGION}b"
}
output "test3" {
  value = "${var.AWS_REGION}c"
}

output "test4" {
  value = var.AWS_REGION
}


output "lb_target_group_arn_suffix" {
  value = aws_lb_target_group.www-cryptostacker-io-tf.arn_suffix
}

output "lb_target_group_arn" {
  value = aws_lb_target_group.www-cryptostacker-io-tf.arn
}

output "lb_target_group_id" {
  value = aws_lb_target_group.www-cryptostacker-io-tf.id
}

output "lb_target_group_name" {
  value = aws_lb_target_group.www-cryptostacker-io-tf.name
}

output "aws_lb_id" {
  value = aws_lb.www-cryptostacker-io-alb-tf.id
}

output "aws_lb_arn" {
  value = aws_lb.www-cryptostacker-io-alb-tf.arn
}

output "aws_lb_arn_suffix" {
  value = aws_lb.www-cryptostacker-io-alb-tf.arn_suffix
}

output "aws_lb_dns_name" {
  value = aws_lb.www-cryptostacker-io-alb-tf.dns_name
}

output "aws_lb_zone_id" {
  value = aws_lb.www-cryptostacker-io-alb-tf.zone_id
}

