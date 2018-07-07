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

## Remove infra

1. Go to infra folder: `cd infra`
2. Run: `terraform destroy`

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

Terraform will generate a list of active users and their passwords in: `infra/users/user-list-result.csv`

# Jumpbox
Jumpbox has the following components running in docker containers:
* Guacamole
* Guacd
* Nginx proxy (dashboard)

## Guacamole

Official `guacamole/guacamole` container is used.

Official guacamole docker container only supports MySQL, PostgreSQL and LDAP backends.
In order to use simple user-mapping.xml user mapping we override default command of the container,
injecting our own custom startup script.

## Nginx proxy (dashboard)
jumpbox is running an nginx proxy to provide access to a dashboard.
It provides basic auth to limit access to users from the workshop.
One login/password for all workshop members is provided for simplicity.

To access the proxy, one needs to open jumpbox public address at port 80:
`http://<jumpbox_uri>`

```
              ________   auth   ___________
internet --> | proxy  | -----> | dashboard |
              --------          -----------
```

Jumpbox also redirects /guacamole to guacamole GUI for convenience.

### Configure proxy URI

Configure dashboard URI in `nginx/conf.d/default.conf`:
```
location /dashboard {
    proxy_pass http://192.168.8.106:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    auth_basic           "Dashboard access";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### Configure proxy user/password
Password is stored in `nginx/.gtpasswd` file. Currently it has current test credentials:
- user: dashboard
- password: dash18BRD!

To set the password do the following:
```
cd jumpbox/nginx
htpasswd -c .htpasswd <user_name>
```

This will update .htpasswd password in local directory.