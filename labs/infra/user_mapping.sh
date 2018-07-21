#!/bin/bash

export USER_COUNT=${USER_COUNT}
export USER_NAME_LIST=${USER_NAME_LIST}

export WORKSTATION_DNS_LIST=${WORKSTATION_DNS_LIST}
export CONTROLLER_DNS_LIST=${CONTROLLER_DNS_LIST}

export SSH_PASSWORD_LIST=${SSH_PASSWORD_LIST}
export CONTROLLER_PASSWORD_LIST=${CONTROLLER_PASSWORD_LIST}

export USER_LIST_FILE_RESULT=${USER_LIST_FILE_RESULT}
export USER_MAPPING_FILE=${USER_MAPPING_FILE}
export USER_HTPASSWD_FILE=${USER_HTPASSWD_FILE}

# functions
generate_password() {
  echo -n $(env LC_CTYPE=C tr -dc "a-zA-Z0-9" < /dev/urandom | head -c 8)
}

add_user() {
  user_id=$1
  user_name=$2
  user_password=$3
  user_password_cnt=$4
  
  user_host_wks=$5
  user_host_cnt=$6
  
  # Add a user-mapping record
  cat >>$USER_MAPPING_FILE<<EOU
  <!-- $user_id - $user_name - WORKSTATION -->
  <authorize username="$user_name" password="$user_password">
    <!-- WORKSTATION -->
    <connection name="Workstation">
      <protocol>ssh</protocol>
      <param name="hostname">$user_host_wks</param>
      <param name="port">22</param>
      <param name="username">$user_name</param>
      <param name="private-key">$(cat ssh/ssh_key)</param>
      <param name="color-scheme">white-black</param>
      <param name="font-size">10</param>
    </connection>
  
    <!-- CONTROLLER -->
    <connection name="Controller">
      <protocol>ssh</protocol>
      <param name="hostname">$user_host_cnt</param>
      <param name="port">22</param>
      <param name="username">$user_name</param>
      <param name="private-key">$(cat ssh/ssh_key)</param>
      <param name="color-scheme">white-black</param>
      <param name="font-size">10</param>
    </connection>
  </authorize>
  
EOU

  # Add a user-list csv record
  echo "$user_name,$user_password,$user_password_cnt,$user_host_wks,$user_host_cnt" >> $USER_LIST_FILE_RESULT

  # Add a user to .htpasswd
  echo $user_password_cnt | htpasswd -i $USER_HTPASSWD_FILE $user_name
}


# main

## parse variables
IFS=',' read -r -a USER_NAME_ARR <<< "$USER_NAME_LIST"

IFS=',' read -r -a WORKSTATION_DNS_ARR <<< "$WORKSTATION_DNS_LIST"
IFS=',' read -r -a CONTROLLER_DNS_ARR <<< "$CONTROLLER_DNS_LIST"

IFS=',' read -r -a SSH_PASSWORD_ARR <<< "$SSH_PASSWORD_LIST"
IFS=',' read -r -a CONTROLLER_PASSWORD_ARR <<< "$CONTROLLER_PASSWORD_LIST"

## generate user-mapping
echo \<user-mapping\> > $USER_MAPPING_FILE
echo 'user,password,password-controller,host_wks,host_cnt' > $USER_LIST_FILE_RESULT
>$USER_HTPASSWD_FILE

echo "Generating users..."
for ((u=0; u<$USER_COUNT; u++));
do
  echo " - User $u/$USER_COUNT - ${USER_NAME_ARR[$u]}"
  add_user $u ${USER_NAME_ARR[$u]} ${SSH_PASSWORD_ARR[$u]} ${CONTROLLER_PASSWORD_ARR[$u]} ${WORKSTATION_DNS_ARR[$u]} ${CONTROLLER_DNS_ARR[$u]}
done

echo \</user-mapping\> >> $USER_MAPPING_FILE