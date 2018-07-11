#
# network.tf
#   configure network for an instance
#

resource "aws_vpc" "default" {
  cidr_block            = "192.168.0.0/16"
  enable_dns_support    = true
  enable_dns_hostnames  = true

  tags = {
    Name = "${var.environment}-vpc"
    environment = "${var.environment}"
  }
}

resource "aws_subnet" "default" {
  vpc_id            = "${aws_vpc.default.id}"
  cidr_block        = "192.168.0.0/20"
  availability_zone = "us-east-1a"

  tags = {
    Name = "${var.environment}-subnet"
    environment = "${var.environment}"
  }
}

resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.default.id}"

  tags = {
    Name = "${var.environment}-gateway"
    environment = "${var.environment}"
  }
}

data "aws_route_table" "default" {
  vpc_id = "${aws_vpc.default.id}"
}

resource "aws_route" "default" {
  route_table_id            = "${data.aws_route_table.default.id}"
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id                = "${aws_internet_gateway.default.id}"
}

# used to peer with AWS S3
//resource "aws_vpc_endpoint" "default" {
//  vpc_id          = "${aws_vpc.default.id}"
//  service_name    = "com.amazonaws.${var.aws_region}.s3"
//  route_table_ids = ["${data.aws_route_table.default.id}"]
//}