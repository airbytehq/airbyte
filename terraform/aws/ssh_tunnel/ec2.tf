# Create a bastion host with a user account we can ssh in as, for using an ssh tunnel.

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

resource "aws_key_pair" "key" {
  key_name   = "dbtunnel-bastion-ec2-user-ssh-key"
  public_key = file("dbtunnel-bastion-ec2-user_rsa.pub")
}

resource "aws_instance" "dbtunnel-bastion" {
  ami           = data.aws_ami.amazon-linux-2.id
  instance_type = "t3.small"

  subnet_id = aws_subnet.main-subnet-public-dbtunnel.id
  vpc_security_group_ids = [aws_security_group.ssh-and-egress-allowed.id]
  key_name = aws_key_pair.key.key_name
  user_data = file("userdata.sh")

  tags = {
    Name = "dbtunnel-bastion"
  }

}

# We're using this for connector testing for now since dns isn't ready.
resource "aws_eip" "dbtunnel-eip" {
  vpc = true
  instance = aws_instance.dbtunnel-bastion.id
}

# TODO: This zone isn't publically resolveable so this ended up not working out right.
data "aws_route53_zone" "selected" {
  name         = "dev.dataline.io."
}

# TODO: This zone isn't publically resolveable so this ended up not working out right.
resource "aws_route53_record" "proxy_cname" {
  name    = "dbtunnel-bastion.${data.aws_route53_zone.selected.name}"
  type    = "A"
  zone_id = data.aws_route53_zone.selected.zone_id
  ttl     = "300"
  records = [aws_instance.dbtunnel-bastion.public_ip]
}

