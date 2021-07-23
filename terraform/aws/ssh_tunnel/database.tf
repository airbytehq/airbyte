# Set up a postgres instance for use in running airbyte connector test cases.

# Tell the database what subnet to belong to, so our ssh tunnel testing finds it in the right place.
resource "aws_db_subnet_group" "default" {
  name       = "dbtunnel-private-dbsubnet-group"
  subnet_ids = [aws_subnet.main-subnet-private-dbtunnel-2a.id, aws_subnet.main-subnet-private-dbtunnel-2b.id]

  tags = {
    Name = "dbtunnel-private-dbsubnet-group"
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

# Create the postgres instance on RDS so it's fully managed and low maintenance
resource "aws_db_instance" "default" {
  allocated_storage    = 5
  availability_zone    = "us-east-2a"
  engine               = "postgres"
  engine_version       = "12.6"
  identifier           = "tunnel-dev"
  instance_class       = "db.t3.small"
  db_subnet_group_name = aws_db_subnet_group.default.name
  name                 = "airbyte"
  username             = "airbyte"
  password             = chomp(file("secrets/aws_db_instance-master-password"))
  parameter_group_name = aws_db_parameter_group.default.name
  skip_final_snapshot  = true
  apply_immediately    = true
}

