variable "sudo_keypair_name" {
  type = string
  description = "Which aws keypair should be used for the sudo-capable user 'ec2-user' on the bastion host"
}
variable "aws_vpc_id" {
  type = string
  description = "Which vpc should the subnets (containing postgres and the bastion) be placed in"
}
variable "subnet_cidr_block1" {
  type = string
  description = "Which private CIDR block should be used for the first subnet"
}
variable "subnet_cidr_block2" {
  type = string
  description = "Which private CIDR block should be used for the second subnet"
}
variable "subnet_az1" {
  type = string
  description = "Which availability zone should be used for the first subnet"
}
variable "subnet_az2" {
  type = string
  description = "Which availability zone should be used for the second subnet"
}
variable "rds_instance_class" {
  type = string
  description = "What instance size should be used for the postgres instance"
}
variable "airbyte_user_authorized_keys_local_filepath" {
  type = string
  description = "Source path for file provisioner to upload the airbyte user's authorized_keys file"
}
