#
# instance.tf
#

# actions before workstation creation
#   - generate key to access workstations from guacamole server
#   - initialize user-mapping.xml and user-list-result.csv files
resource "null_resource" "user_mapping_start" {

  provisioner "local-exec" {
    command = <<EOF
    echo \<user-mapping\> > ${var.user_mapping_file}
    echo 'user,password,host'> ${var.user_list_file_result}

    # Generate ssh-key
    rm -rf ssh/*
    mkdir -p ssh
    ssh-keygen -t rsa -b 2048 -P '' -f ssh/ssh_key -C 'user@example.com'
    EOF
  }
}

resource "null_resource" "user_mapping_body" {
  count       = "${var.workstation_count}"
  depends_on  = ["null_resource.user_mapping_start"]

  provisioner "local-exec" {
    command = <<EOF
    user_id=${count.index}
    user_name=${element(keys(data.external.user_list.result), count.index)}
    user_password=${element(random_string.password.*.result, count.index)}

    user_host_wks=${element(aws_instance.workstation.*.private_dns, count.index)}
    user_host_cnt=${element(aws_instance.controller.*.private_dns, count.index)}

    # Add a user-mapping record
    cat >>${var.user_mapping_file}<<EOU
    <!-- $user_id - $user_name - $user_host_wks - WORKSTATION -->
    <authorize username="$user_name" password="$user_password">
      <!-- WORKSTATION -->
      <connection name="Workstation">
        <protocol>ssh</protocol>
        <param name="hostname">$user_host_wks</param>
        <param name="port">22</param>
        <param name="username">$user_name</param>
        <param name="private-key">$(cat ssh/ssh_key)</param>
        <param name="color-scheme">white-black</param>
        <param name="font-size">10</param>
      </connection>

      <!-- CONTROLLER -->
      <connection name="Controller">
        <protocol>ssh</protocol>
        <param name="hostname">$user_host_cnt</param>
        <param name="port">22</param>
        <param name="username">$user_name</param>
        <param name="private-key">$(cat ssh/ssh_key)</param>
        <param name="color-scheme">white-black</param>
        <param name="font-size">10</param>
      </connection>
    </authorize>
    EOU

    # Add a user url mapping record
    cat >>${var.user_url_mapping_file}<<EOU
    # $user_id - $user_name - $user_host - CONTROLLER
    location /$user_name {
      proxy_pass http://$user_host:80/;
      proxy_set_header Host \$host;
      proxy_set_header X-Real-IP \$remote_addr;

      if (\$remote_user != "$user_name") {
        return 403;
      }

      auth_basic           "Dashboard access";
      auth_basic_user_file /etc/nginx/.htpasswd;
    }

    EOU

    # Add a user-list csv record
    echo "$user_name,$user_password,$user_host" >> ${var.user_list_file_result}
    EOF
  }
}

# actions after workstation creation
#   - finish user-mapping.xml file
resource "null_resource" "user_mapping_end" {
  depends_on    = ["null_resource.user_mapping_body"]

  provisioner "local-exec" {
    command = <<EOF
    echo \</user-mapping\> >> ${var.user_mapping_file}
    EOF
  }
}

resource "aws_instance" "workstation" {
  count         = "${var.workstation_count}"
  ami           = "ami-a4dc46db"
  instance_type = "t2.micro"
  key_name      = "${var.aws_ssh_key_name}"
  depends_on    = ["null_resource.user_mapping_start"]

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

  # add user to user-mapping.xml for guacamole
//  provisioner "local-exec" {
//    command = <<EOF
//user_id=${count.index}
//user_name=${element(keys(data.external.user_list.result), count.index)}
//user_password=${element(random_string.password.*.result, count.index)}
//#'${element(values(data.external.user_list.result), count.index)}'
//user_host=${self.private_dns}
//
//# Add a user-mapping record
//cat >>${var.user_mapping_file}<<EOU
//  <!-- $user_id - $user_name - $user_host - WORKSTATION -->
//  <authorize username="$user_name" password="$user_password">
//    <protocol>ssh</protocol>
//    <param name="hostname">$user_host</param>
//    <param name="port">22</param>
//    <param name="username">$user_name</param>
//    <param name="private-key">$(cat ssh/ssh_key)</param>
//    <param name="color-scheme">white-black</param>
//    <param name="font-size">10</param>
//  </authorize>
//EOU
//
//# Add a user-list csv record
//echo "$user_name,$user_password,$user_host" >> ${var.user_list_file_result}
//EOF
//  }

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
      "sudo rm /tmp/ssh_key.pub"
    ]
  }

  volume_tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-${count.index + 1}-volume",
      "user", "${element(keys(data.external.user_list.result), count.index)}"
    )
  )}"

  tags = "${merge(
    local.common_tags,
    map(
      "Name", "${local.instance_name_runtime}-${count.index + 1}",
      "user", "${element(keys(data.external.user_list.result), count.index)}"
    )
  )}"
}