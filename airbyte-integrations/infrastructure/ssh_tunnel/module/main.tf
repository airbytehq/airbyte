# Create a bastion host with a user account we can ssh in as, for using an ssh tunnel.

# The standard amazon-linux-2 ami will work fine. Don't care about version except stay recent-ish.
data "aws_ami" "amazon-linux-2" {
  owners = [137112412989]

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-2.0.20210701.0-x86_64-gp2"]
  }
}

# Create a host we can ssh into for database ssh tunnel connections from airbyte connectors.
resource "aws_instance" "dbtunnel-bastion" {
  ami           = data.aws_ami.amazon-linux-2.id
  instance_type = "t3.small"

  subnet_id = aws_subnet.main-subnet-public-dbtunnel.id
  vpc_security_group_ids = [aws_security_group.ssh-and-egress-allowed.id]
  key_name = var.sudo_keypair_name
  user_data = file("${path.module}/userdata.sh")
  lifecycle {
    ignore_changes = [associate_public_ip_address]
  }

  tags = {
    Name = "dbtunnel-bastion"
  }

 provisioner "file" {
  source      = var.airbyte_user_authorized_keys_local_filepath
  destination = "/tmp/airbyte_authorized_keys"
  connection {
    type     = "ssh"
    user     = "ec2-user"  # presumes you have the ssh key in your ssh-agent already
    host     = aws_instance.dbtunnel-bastion.public_ip
  }
 }
 provisioner "remote-exec" {
  inline = [
      "sudo bash -cx \"adduser airbyte -m && mkdir /home/airbyte/.ssh && chmod 700 /home/airbyte/.ssh && touch /home/airbyte/.ssh/authorized_keys && chmod 600 /home/airbyte/.ssh/authorized_keys && chown -R airbyte.airbyte /home/airbyte/.ssh && cat /tmp/airbyte_authorized_keys > /home/airbyte/.ssh/authorized_keys && rm /tmp/airbyte_authorized_keys\""
  ]
  connection {
    type     = "ssh"
    user     = "ec2-user"  # presumes you have the ssh private key in your ssh-agent already
    host     = aws_instance.dbtunnel-bastion.public_ip
  }
 }

}

# We're using a static IP for connector testing for now since dns isn't usable for this.
# We would prefer DNS someday.
resource "aws_eip" "dbtunnel-eip" {
  vpc = true
}

resource "aws_eip_association" "dbtunnel-eip-assoc" {
  instance_id = aws_instance.dbtunnel-bastion.id
  allocation_id = aws_eip.dbtunnel-eip.id
}

