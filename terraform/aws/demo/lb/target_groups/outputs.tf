output "airbyte-api-tg" {
  value = aws_lb_target_group.airbyte-api
}

output "airbyte-webapp-tg" {
  value = aws_lb_target_group.airbyte-webapp
}
