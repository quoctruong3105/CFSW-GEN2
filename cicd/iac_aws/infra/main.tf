# --- Full Infrastructure Deployment for AWS Microservices ---

terraform {
  required_version = ">= 1.3"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
  profile = "jenkins-cfsw"
}

# --- VPC ---
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.1"

  name = "microservice-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-southeast-1a", "ap-southeast-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    Terraform   = "true"
    Environment = "prod"
  }
}

resource "aws_db_subnet_group" "db" {
  name       = "microservice-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "Microservice DB Subnet Group"
  }
}

# --- security_groups ---
resource "aws_security_group" "rds_sg" {
  name        = "rds-sg"
  description = "Allow RDS access"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- IAM Role for ECS Tasks ---
resource "aws_iam_role" "ecs_task_exec_role" {
  name_prefix = "ecsTaskExecutionRole-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_exec_policy" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# --- ECS Cluster ---
resource "aws_ecs_cluster" "main" {
  name = "microservices-cluster"
}

# --- ECS Security Group ---
resource "aws_security_group" "ecs_service" {
  name        = "ecs-sg"
  description = "Allow outbound to RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Amazon MQ (RabbitMQ) ---
# resource "aws_mq_broker" "rabbitmq" {
#   broker_name        = "microservice-broker"
#   engine_type        = "RabbitMQ"
#   engine_version     = "3.13"
#   host_instance_type = "mq.t3.micro"

#   auto_minor_version_upgrade = true

#   publicly_accessible = false
#   subnet_ids          = [module.vpc.private_subnets[0]]
#   security_groups     = [module.vpc.default_security_group_id]

#   user {
#     username = "rabbitadmin"
#     password = "StrongRabbit123"
#   }

#   apply_immediately = true
# }

# --- Custom DB Parameter Group to disable SSL ---
resource "aws_db_parameter_group" "postgres_custom" {
  name        = "custom-postgres15"
  family      = "postgres15"
  description = "Custom parameter group with SSL disabled"

  parameter {
    name  = "rds.force_ssl"
    value = "0"
  }
}

# --- RDS PostgreSQL ---
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.3.0"

  identifier                   = "microservice-db"
  engine                       = "postgres"
  engine_version               = "15"
  auto_minor_version_upgrade   = true
  instance_class               = "db.t3.micro"
  allocated_storage            = 20
  max_allocated_storage        = 100

  db_name                      = "appdb"
  username                     = "cfsw_admin"
  manage_master_user_password  = true

  family                       = "postgres15"
  parameter_group_name         = aws_db_parameter_group.postgres_custom.name
  create_db_parameter_group    = false
  create_db_option_group       = false

  db_subnet_group_name         = aws_db_subnet_group.db.name
  vpc_security_group_ids       = [aws_security_group.rds_sg.id]

  publicly_accessible          = false
  skip_final_snapshot          = true
  deletion_protection          = false
}

# --- Application Load Balancer ---
resource "aws_lb" "alb" {
  name               = "microservice-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets
}

resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
