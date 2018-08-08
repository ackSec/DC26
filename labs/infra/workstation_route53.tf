
resource "aws_route53_record" "workstation" {
  count   = "${var.workstation_count}"
  zone_id = "${aws_route53_zone.private.id}" # "${var.zoneID["private"]}" --> private hosted zone is attached to a VPC, in case existing hosted zone is reused, it has to be updated manually
  name    = "${element(keys(data.external.user_list.result), count.index)}-workstation"
  type = "CNAME"
  ttl = "30"
  records = ["${element(aws_instance.workstation.*.private_dns, count.index)}"]
}
