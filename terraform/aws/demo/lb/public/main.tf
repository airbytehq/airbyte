data "aws_security_group" "default-sg" {
  id = var.default-sg
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
}

# Create target groups

module "target-groups" {
  source = "../target_groups"

  name = "${var.name}-public"
  instance-id = var.instance-id
  vpc = var.vpc
}

# Build load balancer

resource "aws_lb" "airbyte-alb" {
  enable_deletion_protection = true

  name               = "${var.name}-airbyte-alb"

  internal           = false
  load_balancer_type = "application"
  security_groups    = [
    data.aws_security_group.default-sg.id,
    aws_security_group.airbyte-alb-sg.id
  ]
  subnets = var.subnets
}

resource "aws_lb_listener" "airbyte-alb-listener" {
  load_balancer_arn = aws_lb.airbyte-alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate

  default_action {
    type             = "forward"
    target_group_arn = module.target-groups.airbyte-webapp-tg.arn
  }
}

# By default we deny all api calls
resource "aws_lb_listener_rule" "deny-all-api" {
  listener_arn = aws_lb_listener.airbyte-alb-listener.arn
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

# Then we allow all the read endpoints
resource "aws_lb_listener_rule" "allow-read-api" {
  listener_arn = aws_lb_listener.airbyte-alb-listener.arn
  priority     = 99

  action {
    type             = "forward"
    target_group_arn = module.target-groups.airbyte-api-tg.arn
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
