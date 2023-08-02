# Setting up a subnet within our main vpc, for ssh tunnel testing.
# We need an ec2 instance (bastion host) reachable from the net with port 22 open for inbound ssh.
# The ec2 instance should be able to download package updates from the public internet, for ease of setup.
#
# We need a postgres instance NOT reachable from the net, but YES reachable from the EC2 instance. 
# AWS lets us set publicly_accessible=false (this is default) on the rds instance 
# to ensure no public IP is assigned to the postgres server.
# That means we can put the postgres server and the bastion host in the same subnet 
# for simplicity, and not have to worry about maintaining route tables.

data "aws_vpc" "main" {
  id = var.aws_vpc_id
}
data "aws_internet_gateway" "default" {
  filter {
    name   = "attachment.vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

# Bastion host sits inside a public subnet
resource "aws_subnet" "main-subnet-public-dbtunnel" {
    vpc_id = data.aws_vpc.main.id
    cidr_block = var.subnet_cidr_block1
    map_public_ip_on_launch = "true" 
    availability_zone = var.subnet_az1
    tags = {
        Name = "public-dbtunnel"
    }
}

# Because an RDS instance requires two AZs we need another subnet for it
resource "aws_subnet" "main-subnet-private-dbtunnel" {
    vpc_id = data.aws_vpc.main.id
    cidr_block = var.subnet_cidr_block2
    map_public_ip_on_launch = "false"
    availability_zone = var.subnet_az2
    tags = {
        Name = "private-dbtunnel"
    }
}


# Output to the public internet
resource "aws_route_table" "dbtunnel-public-route" {
    vpc_id = data.aws_vpc.main.id
    
    route {
        cidr_block = "0.0.0.0/0" 
        gateway_id = data.aws_internet_gateway.default.id
    }
    
    tags = {
        Name = "dbtunnel-public-route"
    }
}

resource "aws_route_table_association" "dbtunnel-route-assoc-public-subnet-1"{
    subnet_id = "${aws_subnet.main-subnet-public-dbtunnel.id}"
    route_table_id = "${aws_route_table.dbtunnel-public-route.id}"
}

resource "aws_route_table_association" "dbtunnel-route-assoc-private-subnet-2"{
    subnet_id = "${aws_subnet.main-subnet-private-dbtunnel.id}"
    route_table_id = "${aws_route_table.dbtunnel-public-route.id}"
}


resource "aws_security_group" "ssh-and-egress-allowed" {
    vpc_id = data.aws_vpc.main.id
    
    egress {
        from_port = 0
        to_port = 0
        protocol = -1
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "ssh-and-egress-allowed"
    }
}


# If we don't provide a security group, RDS picks a default, which won't have our port open.
# So set up a custom security group where we can control the ports open to the database.
resource "aws_security_group" "dbtunnel-sg" {
  name        = "dbtunnel-sg-allow-postgres"
  description = "Allow inbound traffic but only from the dbtunnel subnet"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    description      = "tcp on 5432 from subnet"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = [aws_subnet.main-subnet-public-dbtunnel.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "dbtunnel-sg-allow-postgres"
  }
}

