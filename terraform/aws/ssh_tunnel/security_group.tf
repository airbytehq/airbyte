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
        # TODO: Limit the cidr block for incoming connections here
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "ssh-and-egress-allowed"
    }
}

