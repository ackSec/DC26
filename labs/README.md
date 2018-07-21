# Cloud labs
This script creates cloud infra for a workshop

# Infra
To create the infrastructure you need to set up env variables and run terraform.

Download the latest version of terraform here: [terraform.io](https://www.terraform.io/downloads.html)

1. Set environment variables:
  * TF_VAR_aws_access_key - AWS Access Key
  * TF_VAR_aws_secret_key - AWS Secret Key
  * TF_VAR_aws_ssh_key_name - AWS SSH Key pair name to provision instance with
  * TF_VAR_aws_ssh_key_file - AWS SSH Root key to connect to the instances
  * TF_VAR_workstation_count - Number of workstations to create
2. Go to infra folder: `cd infra`
3. Run `terraform init` (first time only)
4. Run `terraform apply`

## Instance configuration
If you need to configure instance AMI or types, you can change them in the following files:
* `jumpbox.tf` - AMI / instance type for jumpbox. Should be a relatively powerful machine for many connections
* `workstation.tf` - AMI / instance type for user workstations
* `controller.tf` - AMI / instance type for controllers

## Remove infra

1. Go to infra folder: `cd infra`
2. Run: `terraform destroy`

## Multiple environments/labs
It is possible to have multiple environments or labs
Set the following variables:
* TF_VAR_environment
* TF_VAR_lab_name

It is important not to overwrite existing state file.
Use the following syntax to generate a new state file instead of using the default one:
```
terraform apply -state <environment>-<lab_name>.tfstate
terraform destroy -state <environment>-<lab_name>.tfstate
```
For example: `terraform apply -state development-lab01.tfstate`

## Security groups and rights

# Users
https://www.fakenamegenerator.com

Add a list of users to `infra/users/user-list.csv`.
Script will take N names according to amount of workstations. It must be a text file with 1 user name per line.
No headers are permitted, data should start at 1st row.

_example:_
```
johndoe
bob
maxfrank
```

## Passwords

Terraform will generate a list of active users and their passwords in: `infra/users/user-list-result.csv`
Each user has two passwords:
* Password - this is the password for guacamole and SSH access
* Controller Password - this is the password for controller GUI

# Jumpbox
Jumpbox has the following components running in docker containers:
* Guacamole
* Guacd
* Nginx proxy

## Guacamole

Official `guacamole/guacamole` container is used.

Official guacamole docker container only supports MySQL, PostgreSQL and LDAP backends.
In order to use simple user-mapping.xml user mapping we override default command of the container,
injecting our own custom startup script.

## Nginx proxy (dashboard)
jumpbox is running an nginx proxy to provide access to a dashboard.
It provides basic auth to limit access to users from the workshop.
One login/password for all workshop members is provided for simplicity.

To access the proxy, one needs to open jumpbox public address at port 443:
`https://<jumpbox_uri>`

```
              ________   auth   ___________
internet --> | proxy  | -----> | dashboard |
              --------          -----------
```

Jumpbox also redirects /guacamole to guacamole GUI for convenience.

### Self-signed certificate (info)

Generate a self-signed certificate
```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt
```

Generate a Diffie-Hellman group
```
sudo openssl dhparam -out dhparam.pem 1024
```

