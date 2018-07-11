#
# security_group.tf
#   configure a security group for webserver
#

resource "aws_security_group" "controller" {
  count       = "${var.workstation_count}"
  name        = "${var.environment}-${var.lab_name}-controller${count.index + 1}-sg"
  description = "Controller security group"
  vpc_id      = "${aws_vpc.default.id}"

  # Allow SSH from guacamole server
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    security_groups = [ "${aws_security_group.jumpbox.id}" ]
    # DEBUG
    # cidr_blocks = [ "0.0.0.0/0" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # Allow HTTP from guacamole server
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [ "${aws_security_group.jumpbox.id}" ]
    # DEBUG
    # cidr_blocks = [ "0.0.0.0/0" ] # debug: "0.0.0.0/0" "${var.vpc_cidr}"
  }

  # SSH Access for provisioning machine
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [ "${data.external.my_ip.result.ip}/32" ]
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