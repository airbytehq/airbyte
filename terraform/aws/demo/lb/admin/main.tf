data "aws_security_group" "default-sg" {
  id = var.default-sg
}

# Create target groups

module "target-groups" {
  source = "../target_groups"

  name = "${var.name}-admin"
  instance-id = var.instance-id
  vpc = var.vpc
}

# Build load balancer

resource "aws_lb" "airbyte-admin-alb" {
  enable_deletion_protection = true

  name               = "${var.name}-airbyte-admin-alb"

  # lets make sure the admin version can only be accessed internally
  internal           = true

  load_balancer_type = "application"
  security_groups    = [data.aws_security_group.default-sg.id]
  subnets = var.subnets
}

resource "aws_lb_listener" "airbyte-admin-alb-listener" {
  load_balancer_arn = aws_lb.airbyte-admin-alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = module.target-groups.airbyte-webapp-tg.arn
  }
}

resource "aws_lb_listener_rule" "allow-all-api" {
  listener_arn = aws_lb_listener.airbyte-admin-alb-listener.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = module.target-groups.airbyte-api-tg.arn
  }

  condition {
    path_pattern {
      values = [
        "/api/v1/*",
      ]
    }
  }
}
