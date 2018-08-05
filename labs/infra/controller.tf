#
# Controller
#

resource "aws_instance" "controller" {
  count         = "${var.workstation_count}"
  ami           = "ami-10b2b16f"  #"ami-a4dc46db"
  instance_type = "t2.medium"
  key_name      = "${var.aws_ssh_key_name}"
  depends_on    = ["null_resource.ssh_key"]

  associate_public_ip_address = true

  subnet_id                   = "${aws_subnet.default.id}"
  vpc_security_group_ids      = [ "${element(aws_security_group.workstation.*.id, count.index)}" ]

  root_block_device {
    volume_type = "gp2"
    delete_on_termination = true
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = "${file(var.aws_ssh_key_file)}"
  }

  # upload public key to workstation
  provisioner "file" {
    source      = "ssh/ssh_key.pub"
    destination = "/tmp/ssh_key.pub"
  }

  # create workstation user and add keys
  provisioner "remote-exec" {
    inline = [
      "sudo useradd -m -s /bin/bash -p $(echo \"${element(random_string.password.*.result, count.index)}\" | openssl passwd -1 -stdin) ${element(keys(data.external.user_list.result), count.index)}",
      "sudo usermod -aG sudo ${element(keys(data.external.user_list.result), count.index)}",
      "sudo su - ${element(keys(data.external.user_list.result), count.index)} /bin/bash -c 'ls -la /home; mkdir -p $HOME/.ssh; echo \"$(cat /tmp/ssh_key.pub)\" >> $HOME/.ssh/authorized_keys'",
      "cd /home/${element(keys(data.external.user_list.result), count.index)}",
      "sudo apt-get install -y git build-essential ant maven python-dev",
      "sudo git clone https://github.com/ackSec/floodlight.git",
      "cd floodlight",
      "sudo git submodule init",
      "sudo git submodule update",
      "sudo ant",
      "sudo git clone https://github.com/ackSec/floodlight-webui.git",
      "nohup java -jar target/floodlight.jar &",
      "sudo rm /tmp/ssh_key.pub"
    ]
  }
/*
  provisioner "remote-exec" {
    inline = [
      "sudo useradd -m -s /bin/bash -p $(echo \"${element(random_string.password.*.result, count.index)}\" | openssl passwd -1 -stdin) ${element(keys(data.external.user_list.result), count.index)}",
      "sudo usermod -aG sudo ${element(keys(data.external.user_list.result), count.index)}",
      "sudo su - ${element(keys(data.external.user_list.result), count.index)} /bin/bash -c 'ls -la /home; mkdir -p $HOME/.ssh; echo \"$(cat /tmp/ssh_key.pub)\" >> $HOME/.ssh/authorized_keys'",
      "sudo rm /tmp/ssh_key.pub"
    ]
  }
*/
  volume_tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-${count.index + 1}-controller-volume",
      "user", "${element(keys(data.external.user_list.result), count.index)}"
    )
  )}"

  tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-${count.index + 1}-controller",
      "user", "${element(keys(data.external.user_list.result), count.index)}",
      "ssh_key_id", "${null_resource.ssh_key.id}"
    )
  )}"
}
