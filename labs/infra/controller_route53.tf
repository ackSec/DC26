resource "aws_route53_zone" "default" {
  name = "${local.hosted_zone_name}"
  vpc_id = "${aws_vpc.default.id}"
  force_destroy = true

  tags = "${local.common_tags}"
}

resource "aws_route53_record" "instance" {
  count   = "${var.workstation_count}"
  zone_id = "${var.zoneID["private"]}"
  name    = "${element(keys(data.external.user_list.result), count.index)}-controller"
  type    = "CNAME"
  ttl     = "30"

  records = ["${element(aws_instance.controller.*.private_dns, count.index)}"]
}
