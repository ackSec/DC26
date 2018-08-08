resource "aws_route53_record" "jumpbox" {
  zone_id = "${aws_route53_zone.private.id}" # "${var.zoneID["private"]}" --> private hosted zone is attached to a VPC, in case existing hosted zone is reused, it has to be updated manually
  name    = "jumpbox"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.jumpbox.private_ip}"]
}

resource "aws_route53_record" "jumpbox_pub" {
  zone_id = "${var.zoneID["public"]}"

  #depends_on = ["aws_eip.win_jumpbox"]
  name    = "jumpbox"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.jumpbox.public_ip}"]
}
