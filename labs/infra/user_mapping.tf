#
# Nginx and Guacamole user mappings
#

# actions after workstation creation
#   - generate key to access workstations from guacamole server
#   - initialize user-mapping.xml and user-list-result.csv files
resource "null_resource" "user_mapping" {

  provisioner "local-exec" {
    command = "bash user_mapping.sh"

    environment {
      USER_COUNT = "${var.workstation_count}"
      USER_NAME_LIST = "${join(",", keys(data.external.user_list.result))}"
      USER_MAPPING_FILE = "${var.user_mapping_file}"
      WORKSTATION_DNS_LIST = "${join(",", aws_instance.workstation.*.private_dns)}"
      CONTROLLER_DNS_LIST = "${join(",", aws_instance.controller.*.private_dns)}"

      SSH_PASSWORD_LIST = "${join(",", random_string.password.*.id)}"
      CONTROLLER_PASSWORD_LIST = "${join(",", random_string.password_controller.*.id)}"

      USER_LIST_FILE_RESULT = "${var.user_list_file_result}"
      USER_HTPASSWD_FILE = "${var.user_htpasswd_file}"
    }

  }
}