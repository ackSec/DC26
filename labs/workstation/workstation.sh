#!/bin/bash

export DOCKER_REPO_KEY_FINGERPRINT='9DC858229FC7DD38854AE2D88D81803C0EBFCD88'
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
  sudo apt-get update
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

add_images(){
  log "Adding images..."
  sudo service docker start
  sudo docker pull acksec/snort:latest
  sudo docker pull acksec/dc26:latest
}

start_images(){
  log "Starting images..."
  sudo docker run -w /root/ -itd -e CONTROLLER_IP=$CONTROLLER_IP --name attacher acksec/dc26
  sudo docker run -w /opt/ -itd -e CONTROLLER_IP=$CONTROLLER_IP --name victim acksec/snort
}

# main
log " *** Installing Docker on Workstation... ***"

## install dependencies
log " *** Pulling Images ***"
install_docker
  verify_exitcode 'install_docker'

## run
add_images
  verify_exitcode 'add_images'

log " *** Workstation started ***"
