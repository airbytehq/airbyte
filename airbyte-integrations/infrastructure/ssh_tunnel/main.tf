# Set up a subnet with bastion and postgres so we can test inbound ssh tunnel behavior from connectors.

# ec2-user needs login creds
resource "aws_key_pair" "key" {
  key_name   = "dbtunnel-bastion-ec2-user-ssh-key"
  public_key = file("${path.module}/user_ssh_public_keys/dbtunnel-bastion-ec2-user_rsa.pub")
}

# Sets up the bastion host, an unprivileged airbyte shell user, and postgres
module "ssh_tunnel_testing" {
  source = "./module"

  airbyte_user_authorized_keys_local_filepath = "user_ssh_public_keys/dbtunnel-bastion-airbyte_rsa.pub"
  
  aws_vpc_id = "vpc-001ad881b80193126"
  sudo_keypair_name = aws_key_pair.key.key_name

  subnet_az1 = "us-east-2a"
  subnet_cidr_block1 = "10.0.40.0/24"

  subnet_az2 = "us-east-2b"
  subnet_cidr_block2 = "10.0.41.0/24"

  rds_instance_class = "db.t3.small"

  // Outputs: bastion_ip_addr postgres_endpoint_fqdn_with_port

}

