# Sets up a postgres instance for use in running airbyte connector test cases.


# Tell the database what subnet to belong to, so it joins the right subnets and is routable from the bastion.
# AWS insists on a minimum of two availability zones for an RDS instance even if we don't care about high availability.
resource "aws_db_subnet_group" "default" {
  name       = "dbtunnel-public-dbsubnet-group"
  subnet_ids = [aws_subnet.main-subnet-public-dbtunnel.id, aws_subnet.main-subnet-private-dbtunnel.id]

  tags = {
    Name = "dbtunnel-public-dbsubnet-group"
  }
}

# This is mainly a placeholder for settings we might want to configure later.
resource "aws_db_parameter_group" "default" {
  name        = "rds-pg"
  family      = "postgres12"
  description = "RDS default parameter group"

  #parameter {
  #  name  = "character_set_client"
  #  value = "utf8"
  #}
}

# Create the postgres instance on RDS so it's fully managed and low maintenance.
# For now all we care about is testing with postgres.
resource "aws_db_instance" "default" {
  allocated_storage    = 5
  engine               = "postgres"
  engine_version       = "12.6"
  identifier           = "tunnel-dev"
  instance_class       = var.rds_instance_class
  db_subnet_group_name = aws_db_subnet_group.default.name 
  name                 = "airbyte"
  username             = "airbyte"
  password             = chomp(file("${path.module}/secrets/aws_db_instance-master-password"))
  parameter_group_name = aws_db_parameter_group.default.name
  publicly_accessible = false
  skip_final_snapshot  = true
  apply_immediately    = true
  vpc_security_group_ids = [aws_security_group.dbtunnel-sg.id]
}

