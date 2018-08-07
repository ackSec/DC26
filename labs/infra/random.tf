#
# Random
#

resource "random_string" "password" {
  count   = "${var.workstation_count}"
  length  = 6
  special = false
  upper   = false
  number  = false

  # override_special = "/@\" "
}

resource "random_string" "password_controller" {
  count   = "${var.workstation_count}"
  length  = 6
  special = false
  upper   = false
  number  = false

  # override_special = "/@\" "
}
