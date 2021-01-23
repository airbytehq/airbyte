data "aws_vpc" "vpc" {
  id = var.vpc
}

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
