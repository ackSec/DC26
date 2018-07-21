#!/bin/bash

export DOCKER_REPO_KEY_FINGERPRINT='9DC858229FC7DD38854AE2D88D81803C0EBFCD88'
export DOCKER_STACK_NAME='guacamole-server'
export DOCKER_VOLUME_DB_VOLUME_NAME="${DOCKER_STACK_NAME}_db-volume"

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export LOG_FILE='/var/log/jumpbox.log'

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
>$LOG_FILE
exec >  >(sudo tee -ia $LOG_FILE)
exec 2> >(sudo tee -ia $LOG_FILE)

log() {
  echo "$(date) ~> $@"
}

verify_exitcode() {
  exitcode=$?
  msg="$@"
  if [ $exitcode -ne 0 ]
  then
    log "ERROR: operation ($msg) returned non-zero exit code ($exitcode)!"
    exit 1
  fi
}

install_docker() {
  log "Installing docker..."
  sudo apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      software-properties-common

  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

  docker_fp=$(sudo apt-key fingerprint 0EBFCD88 | grep 'Key fingerprint' | sed 's/.* = //g' | sed 's/ //g')
  test ${DOCKER_REPO_KEY_FINGERPRINT} != ${docker_fp} && \
    echo "ERROR: obtained docker repo fingerprint (${docker_fp}) differs ${DOCKER_REPO_KEY_FINGERPRINT}" && \
    exit 1

  sudo add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) \
     stable"

  sudo apt-get update
  sudo apt-get install -y docker-ce
}

generate_ssh_cert() {
  log "Generating SSL cert..."
  mkdir -p /etc/ssl/certs
  pushd /etc/ssl/certs
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt -subj "/C=US/ST=SomeState/L=SomeCity/O=Labs/CN=rubuscloud.com"
    sudo openssl dhparam -out dhparam.pem 1024
  popd
}

# main
log " *** Starting jumpbox... ***"
cd $SCRIPT_DIR

## install dependencies
install_docker
  verify_exitcode 'install_docker'

## generate certs for nginx
generate_ssh_cert
  verify_exitcode 'generate_ssh_cert'

## run
sudo docker swarm init
sudo docker stack deploy -c docker-compose.yml $DOCKER_STACK_NAME
  verify_exitcode 'docker stack deploy'

log " *** Jumpbox started ***"