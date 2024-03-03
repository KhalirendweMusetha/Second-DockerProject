provider "aws" {
  region = var.region
}

resource "aws_key_pair" "cloud_guru" {
  key_name   = var.key_name
  public_key = file("~/.ssh/cloud_guru.pub")
}

resource "aws_security_group" "instance_security_group" {
  name        = "allow_ssh"
  description = "Security group to allow SSH access"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["34.248.107.221/32"]
  }

  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["34.248.107.221/32"]
  }
    ingress {
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["34.248.107.221/32"]
  }
      ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["34.248.107.221/32"]
  }
        ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["34.248.107.221/32"]
  }
     ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# get template file
# data "template_file" "user_data" {
#   template = file("user_data.tpl")
# }

resource "aws_instance" "prometheus_ec2" {
  ami           =  var.ami_id// Linux 2 AMI ID in your region
  instance_type = var.instance_type
  key_name      = aws_key_pair.cloud_guru.key_name
  security_groups = [aws_security_group.instance_security_group.name]

  #user_data = data.template_file.user_data.rendered
    provisioner "file" {
    source      = "bash.sh"
    destination = "/tmp/bash.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/bash.sh",
      "/tmp/bash.sh"
    ]
  }
    connection {
    type        = "ssh"
    user        = "ec2-user"  # or the appropriate username for your AMI
    private_key = file("~/.ssh/cloud_guru")
    host        = self.public_ip
  }
  associate_public_ip_address = true
}

output "instance_public_ip" {
  value = aws_instance.prometheus_ec2.public_ip
}
