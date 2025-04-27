output "db_endpoint" {
  value = module.db.db_instance_address
}

output "db_user" {
  value = "cfsw_admin"
}

output "rds_master_secret_arn" {
  value     = module.db.db_instance_master_user_secret_arn
  sensitive = true
}

output "ecs_cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "ecs_sg_id" {
  value = aws_security_group.ecs_service.id
}

output "alb_dns" {
  value = aws_lb.alb.dns_name
}

output "alb_arn" {
  value = aws_lb.alb.arn
}

output "alb_sg_id" {
  value = aws_security_group.alb_sg.id
}

# output "mq_endpoint" {
#   value = aws_mq_broker.rabbitmq.instances[0].endpoints[0]
# }

output "ecs_task_exec_role_arn" {
  value = aws_iam_role.ecs_task_exec_role.arn
}
