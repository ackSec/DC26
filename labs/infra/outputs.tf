#
# outputs.tf
#   defines outputs which are printed out after terraform run

output "workstation_id" {
  value = "${aws_instance.workstation.*.id}"
}

output "jumpbox_id" {
  value = "${aws_instance.jumpbox.*.id}"
}

output "jumpbox_public_dns" {
  value = "${aws_instance.jumpbox.*.public_dns}"
}

output "my_ip" {
  value = "${data.external.my_ip.result.ip}"
}

output "user_list" {
  value = "User list can be found at users/user-list-result.csv"
}