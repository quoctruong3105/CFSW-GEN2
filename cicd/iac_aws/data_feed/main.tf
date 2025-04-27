provider "aws" {
  region  = "ap-southeast-1"
  profile = "jenkins-cfsw"
}

resource "aws_cloudwatch_log_group" "database_init" {
  name              = "/ecs/database-init"
  retention_in_days = 3
}

resource "aws_cloudwatch_log_group" "data_feed" {
  name              = "/ecs/data-feed"
  retention_in_days = 3
}

data "aws_secretsmanager_secret_version" "rds_secret" {
  secret_id = var.rds_master_secret_arn.value
}

locals {
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.rds_secret.secret_string)
}

# --- ECS Task Definition ---
resource "aws_ecs_task_definition" "database_init" {
  family                   = "database-init-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_task_exec_role_arn.value

  container_definitions = jsonencode([{
    name        = "database-init"
    image       = "truongnq31/cfsw_db_init"
    essential   = true
    environment = [
      { name = "DB_HOST",     value = var.db_endpoint.value },
      { name = "DB_USER",     value = var.db_user.value },
      { name = "DB_NAME",     value = "appdb" },
      { name = "DB_PASSWORD", value = local.db_credentials["password"] }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/database-init"
        awslogs-region        = "ap-southeast-1"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

resource "aws_ecs_task_definition" "data_feed" {
  family                   = "data-feed-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_task_exec_role_arn.value

  container_definitions = jsonencode([{
    name        = "data-feed"
    image       = "truongnq31/data_feed"
    essential   = true
    environment = [
      { name = "DB_HOST",     value = var.db_endpoint.value },
      { name = "DB_USER",     value = var.db_user.value },
      { name = "DB_NAME",     value = "appdb" },
      { name = "DB_PASSWD", value = local.db_credentials["password"] }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/data-feed"
        awslogs-region        = "ap-southeast-1"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

# --- Run database_init Task Once ---
resource "null_resource" "run_database_init" {
  depends_on = [aws_ecs_task_definition.database_init]

  provisioner "local-exec" {
    command = "aws ecs run-task --profile jenkins-cfsw --cluster ${var.ecs_cluster_id.value} --launch-type FARGATE --network-configuration awsvpcConfiguration={subnets=[\"${join("\",\"", var.private_subnets.value)}\"],securityGroups=[\"${var.ecs_sg_id.value}\"],assignPublicIp=\"DISABLED\"} --task-definition ${aws_ecs_task_definition.database_init.arn} --region ap-southeast-1"
  }

  triggers = {
    always_run = timestamp()
  }
}

# --- Run data_feed Task Once ---
resource "null_resource" "run_data_feed" {
  depends_on = [
    aws_ecs_task_definition.data_feed,
    null_resource.run_database_init
  ]

  provisioner "local-exec" {
    command = "aws ecs run-task --profile jenkins-cfsw --cluster ${var.ecs_cluster_id.value} --launch-type FARGATE --network-configuration awsvpcConfiguration={subnets=[\"${join("\",\"", var.private_subnets.value)}\"],securityGroups=[\"${var.ecs_sg_id.value}\"],assignPublicIp=\"DISABLED\"} --task-definition ${aws_ecs_task_definition.data_feed.arn} --region ap-southeast-1"
  }

  triggers = {
    always_run = timestamp()
  }
}

