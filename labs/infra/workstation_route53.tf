resource "aws_route53_record" "workstation" {
  count   = "${var.workstation_count}"
  zone_id = "${var.zoneID["private"]}"
  name    = "${element(keys(data.external.user_list.result), count.index)}-workstation"
  type    = "CNAME"
  ttl     = "30"
  records = ["${element(aws_instance.workstation.*.private_dns, count.index)}"]
}
