#
# Random
#

resource "random_string" "password" {
  count = "${var.workstation_count}"
  length = 6
  special = false
  # override_special = "/@\" "
}
