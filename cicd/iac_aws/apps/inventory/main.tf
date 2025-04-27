provider "aws" {
  region  = "ap-southeast-1"
  profile = "jenkins-cfsw"
}

data "aws_secretsmanager_secret_version" "rds_secret" {
  secret_id = var.rds_master_secret_arn.value
}

locals {
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.rds_secret.secret_string)
}

# --- ECS Task Definition ---
resource "aws_ecs_task_definition" "inventory" {
  family                   = "inventory-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_task_exec_role_arn.value

  container_definitions = jsonencode([{
    name  = "inventory"
    image = "truongnq31/inventory:beta"
    portMappings = [{ containerPort = 80 }]
    environment = [
      { name = "SERVICE_NAME", value = "Inventory" },
      { name = "DB_HOST", value = var.db_endpoint.value },
      { name = "DB_NAME", value = "inventory" },
      { name = "DB_USER", value = "cfsw_admin" },
      { name = "DB_PASSWORD", value = local.db_credentials["password"] },
      { name = "DB_PORT", value = "5432" },
      # { name = "EVENT_BUS_HOST", value = var.mq_endpoint.value },
      { name = "INVENTORY_SERVICE_URL", value = "http://${var.alb_dns.value}/inventory" }
    ]
  }])
}

# --- Target Group for Inventory ---
resource "aws_lb_target_group" "inventory" {
  name        = "tg-inventory"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id.value

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# --- Listener (Default returns 404) ---
resource "aws_lb_listener" "http" {
  load_balancer_arn = var.alb_arn.value
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Not Found"
      status_code  = "404"
    }
  }
}

# --- Listener Rule for /inventory* path ---
resource "aws_lb_listener_rule" "inventory" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.inventory.arn
  }

  condition {
    path_pattern {
      values = ["/inventory", "/inventory*"]
    }
  }
}

# --- ECS Service ---
resource "aws_ecs_service" "inventory" {
  name            = "inventory-service"
  cluster         = var.ecs_cluster_id.value
  task_definition = aws_ecs_task_definition.inventory.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = var.private_subnets.value
    security_groups = [var.ecs_sg_id.value]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.inventory.arn
    container_name   = "inventory"
    container_port   = 80
  }

  depends_on = [aws_lb_target_group.inventory]
}
