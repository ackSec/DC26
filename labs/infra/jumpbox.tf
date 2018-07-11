#
# instance.tf
#

resource "aws_instance" "jumpbox" {
  ami           = "ami-a4dc46db"
  instance_type = "t2.micro"
  key_name      = "${var.aws_ssh_key_name}"
  depends_on    = ["aws_instance.workstation"]

  associate_public_ip_address = true

  subnet_id                   = "${aws_subnet.default.id}"
  vpc_security_group_ids      = [ "${aws_security_group.jumpbox.id}" ]

  root_block_device {
    volume_type = "gp2"
//    volume_size = "10"
    delete_on_termination = true
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = "${file(var.aws_ssh_key_file)}"
  }

  # copy generated files to guacamole and nginx
  provisioner "local-exec" {
    command = <<EOF
      cp ${var.user_mapping_file} ../jumpbox/guacamole/
      cp ${var.user_url_mapping_file} ../jumpbox/nginx/include/
    EOF
  }

  provisioner "remote-exec" {
    inline = [
      "sudo mkdir /opt/jumpbox",
      "sudo chown ubuntu:root /opt/jumpbox"
    ]
  }

  provisioner "file" {
    source      = "../jumpbox/"
    destination = "/opt/jumpbox"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo bash /opt/jumpbox/jumpbox.sh"
    ]
  }

  volume_tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-jumpbox-volume"
    )
  )}"

  tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-jumpbox"
    )
  )}"
}