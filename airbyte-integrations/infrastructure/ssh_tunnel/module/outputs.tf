output "bastion_ip_addr" {
  value = aws_instance.dbtunnel-bastion.public_ip
}
output "postgres_endpoint_fqdn_with_port" {
  value = aws_db_instance.default.endpoint
}

