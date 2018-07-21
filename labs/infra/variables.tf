#
# variaibles.tf
#   to override default settings defined here, set env variables with same names starting with TF_VAR_<variable name>
#   more info in terraform documentation: https://www.terraform.io/intro/getting-started/variables.html

# aws provider vars
variable "aws_access_key" {
  description = "Access key for Amazon AWS account"
  default = "override me from env var TF_VAR_aws_access_key"
}

variable "aws_secret_key" {
  description = "Secret key for Amazon AWS account"
  default = "override me from env var TF_VAR_aws_secret_key"
}

variable "aws_ssh_key_name" {
  description = "SSH key file to provision aws instances"
  default = "gp42.aws2.root201802"
}

variable "aws_ssh_key_file" {
  description = "SSH key file to access aws instances"
  default = "/Users/gp/.aws/gp42.aws2.root201802"
}

variable "aws_region" {
  description = "Region where the AWS resource will be created"
  default = "us-east-1"
}

# General configuration
variable "environment" {
  description = "Environment name"
  default = "development"
}

variable "lab_name" {
  description = "Lab name"
  default = "testlab01"
}

## instance configuration
variable "workstation_count" {
  description = "Specify amount of workstations"
  default = "2"
}

## users
variable "user_mapping_file" {
  description = "User-mapping.xml file name"
  default = "users/user-mapping.xml"
}

variable "user_htpasswd_file" {
  description = ".htpasswords file name used for basic authentication on Nginx"
  default = "users/.htpasswd"
}

variable "user_list_file" {
  description = "List of users"
  default = "users/user-list.csv"
}

variable "user_list_file_result" {
  description = "List of active users"
  default = "users/user-list-result.csv"
}