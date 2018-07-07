#
# providers.tf
#   defines providers for tf

provider "aws" {
  version     = "= 1.2"
  access_key  = "${var.aws_access_key}"
  secret_key  = "${var.aws_secret_key}"
  region      = "${var.aws_region}"
}