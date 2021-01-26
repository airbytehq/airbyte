data "aws_security_group" "default-sg" {
  id = var.default-sg
}

data "aws_ami" "amazon-linux-2" {
  # Hardcoded 'Amazon' owner id
  owners = [137112412989]
  most_recent = true

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-2*"]
  }
}

# Ensure we can ssh to the airbyte instance
resource "aws_security_group" "airbyte-ssh-sg" {
  name        = "${var.name}-airbyte-ssh-sg"
  description = "Allow ssh traffic"

  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "airbyte-instance" {
  lifecycle {
    prevent_destroy = true
  }

  instance_type = var.instance-size
  ami           = data.aws_ami.amazon-linux-2.id

  security_groups = [
    data.aws_security_group.default-sg.name,
    aws_security_group.airbyte-ssh-sg.name
  ]

  key_name = var.key-name

  user_data = file("${path.module}/init.sh")

  tags = {
    Name = "${var.name}-airbyte-app"
  }
}
