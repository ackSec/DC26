#
# Controller
#

resource "aws_instance" "controller" {
  count         = "${var.workstation_count}"
  #ami           = "ami-a4dc46db" # public ubuntu image
  ami           = "ami-10b2b16f" # private controller image
  instance_type = "t2.medium"
  key_name      = "${var.aws_ssh_key_name}"
  depends_on    = ["null_resource.ssh_key"]

  associate_public_ip_address = true

  subnet_id              = "${aws_subnet.default.id}"
  vpc_security_group_ids = ["${element(aws_security_group.workstation.*.id, count.index)}"]

  root_block_device {
    volume_type           = "gp2"
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

  provisioner "file" {
    content     = "${element(data.template_file.floodlight_init.*.rendered, count.index)}"
    destination = "/tmp/floodlight"
  }

  # create workstation user and add keys
  provisioner "remote-exec" {
    inline = [
      "export user=${element(keys(data.external.user_list.result), count.index)}",
      "sudo useradd -m -s /bin/bash -p $(echo \"${element(random_string.password.*.result, count.index)}\" | openssl passwd -1 -stdin) $user",
      "sudo usermod -aG sudo $user",
      "sudo su - $user /bin/bash -c 'ls -la /home; mkdir -p $HOME/.ssh; echo \"$(cat /tmp/ssh_key.pub)\" >> $HOME/.ssh/authorized_keys'",
      "sudo rm /tmp/ssh_key.pub",
      "sudo mv /home/ubuntu/floodlight /opt/floodlight",  # image ami-10b2b16f
      "sudo chown $user:$user /opt/floodlight",           # image ami-10b2b16f
      "sudo chmod -R 755 /opt/floodlight",                # image ami-10b2b16f
      "sudo mv /tmp/floodlight /etc/init.d/floodlight",   # image ami-10b2b16f
      "sudo chmod +x /etc/init.d/floodlight",             # image ami-10b2b16f
      "sudo /etc/init.d/floodlight start"                 # image ami-10b2b16f
#
# Compilation example:
#
//      "sudo apt-get update", # compilation tools were not installed because of this
//      "sudo apt-get install -y git build-essential ant maven python-dev openjdk-8-jdk",
//      "cd /tmp",
//      "sudo -s -u $user /bin/bash -c 'git clone https://github.com/ackSec/floodlight.git'", # Switching to user to get correct rights
//      "sudo mv floodlight /opt/",
//      "sudo sudo chown $user:$user /opt/floodlight",
//      "sudo chmod -R 755 /opt/floodlight",
//      "sudo mv /tmp/floodlight /etc/init.d/floodlight",
//      "sudo chmod +x /etc/init.d/floodlight",
//      "cd /opt/floodlight",
//      "sudo -s -u $user /bin/bash -c 'git submodule init; git submodule update; ant'", # compile
//      "sudo -s -u $user /bin/bash -c 'git clone https://github.com/ackSec/floodlight-webui.git'",
//      "echo ' *** Starting controller process ***'",
//      "sudo /etc/init.d/floodlight start"
    ]
  }

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