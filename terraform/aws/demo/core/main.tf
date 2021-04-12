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

  filter {
    name   = "image-id"
    values = [var.ami_id]
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
    # If you need to destroy the instance, make sure you back up the airbyte configuration.
    prevent_destroy = true
    # So we can edit the init.sh script without having to re-create the instance.
    ignore_changes = [user_data]
  }

  instance_type = var.instance-size
  ami           = data.aws_ami.amazon-linux-2.id

  security_groups = [
    data.aws_security_group.default-sg.name,
    aws_security_group.airbyte-ssh-sg.name
  ]

  key_name = var.key-name

  user_data = file("${path.module}/init.sh")

  root_block_device {
    volume_size = 60
  }

  tags = {
    Name = "${var.name}-airbyte-app"
  }
}
