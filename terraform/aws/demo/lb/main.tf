data "aws_security_group" "default-sg" {
  id = var.default-sg
}

data "aws_vpc" "vpc" {
  id = var.vpc
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

resource "aws_lb_target_group" "airbyte-webapp" {
  name     = "${var.name}-airbyte-webapp-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id = data.aws_vpc.vpc.id

  health_check {
    path = "/"
  }
}

resource "aws_lb_target_group_attachment" "airbyte-webapp" {
  target_group_arn = aws_lb_target_group.airbyte-webapp.arn
  target_id        = var.instance-id
  port             = 8000
}

resource "aws_lb_target_group" "airbyte-api" {
  name     = "${var.name}-airbyte-api-tg"
  port     = 8001
  protocol = "HTTP"
  vpc_id = data.aws_vpc.vpc.id

  health_check {
    path = "/api/v1/health"
  }
}

resource "aws_lb_target_group_attachment" "airbyte-api" {
  target_group_arn = aws_lb_target_group.airbyte-api.arn
  target_id        = var.instance-id
  port             = 8001
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
    target_group_arn = aws_lb_target_group.airbyte-webapp.arn
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
    target_group_arn = aws_lb_target_group.airbyte-api.arn
  }

  condition {
    path_pattern {
      values = [
        "/api/v1/*/list",
        "/api/v1/*/list_latest",
        "/api/v1/*/get",
        "/api/v1/*/get_by_slug",
        "/api/v1/health",
      ]
    }
  }
}

# Check for secret cookie to enable write
resource "aws_lb_listener_rule" "allow-all-api" {
  listener_arn = aws_lb_listener.airbyte-alb-listener.arn
  priority     = 98

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airbyte-api.arn
  }

  condition {
    http_header {
      http_header_name = "cookie"
      values = ["*hack-auth-token=${var.auth-secret}*"]
    }
  }

  condition {
    path_pattern {
      values = [
        "/api/v1/*"
      ]
    }
  }
}

# Auth hack

# By default we deny all api calls
resource "aws_lb_listener_rule" "auth-hack" {
  listener_arn = aws_lb_listener.airbyte-alb-listener.arn
  priority     = 97

  action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/html"
      message_body = file("${path.module}/auth.html")
      status_code  = "200"
    }
  }

  condition {
    path_pattern {
      values = ["/hack/auth"]
    }
  }
}
