#
# security_group.tf
#   configure a security group for webserver
#

resource "aws_security_group" "jumpbox" {
  name        = "${var.environment}-${var.lab_name}-jumpbox-sg"
  description = "Workstation security group"
  vpc_id      = "${aws_vpc.default.id}"

  # Allow HTTP (nginx proxy)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [ "0.0.0.0/0" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # Allow HTTPS (nginx proxy)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [ "0.0.0.0/0" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # Allow HTTP (nginx controller proxy)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [ "0.0.0.0/0" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # SSH Access for provisioning machine
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [ "${data.external.my_ip.result.ip}/32" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # Allow ALL outbound
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = [ "0.0.0.0/0" ]
  }

  tags = {
    environment = "${var.environment}"
  }
}