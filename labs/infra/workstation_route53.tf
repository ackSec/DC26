/*
resource "aws_route53_record" "workstation" {
  zone_id = "${var.zoneID["private"]}"
  name = "workstation"
  type = "A"
  ttl = "300"
  records = ["${aws_instance.workstation.private_ip}"]
}
*/
