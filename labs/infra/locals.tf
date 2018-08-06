#
# common_tags.tf
#

locals {
  instance_name_runtime = "${var.environment}-${var.lab_name}"
  hosted_zone_name = "${var.environment}-${var.lab_name}-intra.net"

  common_tags = {
    environment = "${var.environment}"
    lab_name    = "${var.lab_name}"
  }
}
