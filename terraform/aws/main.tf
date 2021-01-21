variable "name" {
  type = string
  default = "demo"
}

variable "vpc" {
  type = string
  default = "vpc-0e436274"
}

variable "subnets" {
  default = [
    "subnet-8a7d68ed",
    "subnet-2f45e062",
    "subnet-2eca9310",
    "subnet-cf8393e1",
    "subnet-64f0e638",
    "subnet-e9f33ce7"
  ]
}

variable "key_name" {
  type = string
  default = "airbyte-app"
}

variable "certificate" {
  type = string
  default = "arn:aws:acm:us-east-1:168714685353:certificate/c762da95-be91-466d-a9f0-1c22f449ae0d"
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.24.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  shared_credentials_file = "~/.aws/credentials"
}

data "aws_ami" "amazon-linux-2" {
  owners = [137112412989]
  most_recent = true

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-2*"]
  }
}

resource "aws_security_group" "airbyte-instance-sg" {
  name        = "${var.name}-airbyte-instance-sg"
  description = "Allow traffic to the airbyte instance"

  ingress {
    description = "http-webapp"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    security_groups = [aws_security_group.airbyte-alb-sg.id]
  }

  ingress {
    description = "http-api"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    security_groups = [aws_security_group.airbyte-alb-sg.id]
  }

  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
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

resource "aws_instance" "airbyte-instance" {
  instance_type = "t3.medium"
  ami           = data.aws_ami.amazon-linux-2.id

  security_groups = [aws_security_group.airbyte-instance-sg.name]

  key_name = var.key_name

  user_data = file("${path.module}/init.sh")

  tags = {
    Name = "${var.name}-airbyte-app"
  }
}

resource "aws_security_group" "airbyte-alb-sg" {
  name        = "${var.name}-airbyte-alb-sg"
  description = "Allow traffic to the elb"

  ingress {
    description = "https"
    from_port   = 443
    to_port     = 443
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

resource "aws_lb" "airbyte-alb" {
  enable_deletion_protection = true

  name               = "${var.name}-airbyte-alb"

  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.airbyte-alb-sg.id]
  subnets = var.subnets
}

resource "aws_lb_target_group" "airbyte-webapp" {
  name     = "${var.name}-airbyte-webapp-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id = var.vpc

  health_check {
    path = "/"
  }
}

resource "aws_lb_target_group_attachment" "airbyte-webapp" {
  target_group_arn = aws_lb_target_group.airbyte-webapp.arn
  target_id        = aws_instance.airbyte-instance.id
  port             = 8000
}

resource "aws_lb_target_group" "airbyte-api" {
  name     = "${var.name}-airbyte-api-tg"
  port     = 8001
  protocol = "HTTP"
  vpc_id = var.vpc

  health_check {
    path = "/api/v1/health"
  }
}

resource "aws_lb_target_group_attachment" "airbyte-api" {
  target_group_arn = aws_lb_target_group.airbyte-api.arn
  target_id        = aws_instance.airbyte-instance.id
  port             = 8001
}

resource "aws_lb_listener" "airbyte-app" {
  load_balancer_arn = aws_lb.airbyte-alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airbyte-webapp.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.airbyte-app.arn
  priority     = 99

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airbyte-api.arn
  }

  condition {
    path_pattern {
      values = [
        "/api/v1/*/list",
        "/api/v1/*/get",
        "/api/v1/*/get_by_slug",
        "/api/v1/*/health",
      ]
    }
  }
}

resource "aws_lb_listener_rule" "roapi" {
  listener_arn = aws_lb_listener.airbyte-app.arn
  priority     = 100

  action {
    type = "fixed-response"

    fixed_response {
      content_type = "application/json"
      message_body = "{}"
      status_code  = "401"
    }
  }

  condition {
    path_pattern {
      values = ["/api/v1/*"]
    }
  }
}
