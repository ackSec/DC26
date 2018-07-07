#
# common_tags.tf
#

locals {
  instance_name_runtime = "${var.environment}-${var.lab_name}"

  common_tags = {
    environment = "${var.environment}"
    lab_name    = "${var.lab_name}"
  }
}