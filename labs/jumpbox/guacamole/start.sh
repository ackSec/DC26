#!/bin/bash

# params


# functions
log() {
  echo "$(date)~> $@"
}

### check if guacd exists
#check_guacd() {
#  log "Checking if guacd exists..."
#  # Use default guacd port if none specified
#  export GUACD_PORT="${GUACD_PORT-4822}"
#
#  # Verify required guacd connection information is present
#  if [ -z "$GUACD_HOSTNAME" -o -z "$GUACD_PORT" ]; then
#    cat <<END
#FATAL: Missing GUACD_HOSTNAME or "guacd" link.
#-------------------------------------------------------------------------------
#Every Guacamole instance needs a corresponding copy of guacd running. To
#provide this, you must either:
#
#(a) Explicitly link that container with the link named "guacd".
#
#(b) If not using a Docker container for guacd, explicitly specify the TCP
#    connection information using the following environment variables:
#
#GUACD_HOSTNAME     The hostname or IP address of guacd. If not using a guacd
#                   Docker container and corresponding link, this environment
#                   variable is *REQUIRED*.
#
#GUACD_PORT         The port on which guacd is listening for TCP connections.
#                   This environment variable is optional. If omitted, the
#                   standard guacd port of 4822 will be used.
#END
#    exit 1;
#  fi
#
#}

###
### jumpbox directory is preloaded by terraform to /tmp/jumpbox
###
#get_jumpbox() {
#  mv /tmp/jumpbox /opt
#}

##
## Starts Guacamole under Tomcat, replacing the current process with the
## Tomcat process. As the current process will be replaced, this MUST be the
## last function run within the script.
##
start_guacamole() {
  log "Starting guacamole..."
  # Install webapp
  rm -rf $CATALINA_HOME/webapps/ROOT/*
  cat >$CATALINA_HOME/webapps/ROOT/index.jsp<<EOF
<%
    String redirectURL = "/guacamole";
    response.sendRedirect(redirectURL);
%>
EOF
  ln -sf /opt/guacamole/guacamole.war $CATALINA_HOME/webapps/guacamole.war

  # Start tomcat
  cd /usr/local/tomcat
  exec catalina.sh run
}


# main
log 'Running start.sh...'
#get_jumpbox
start_guacamole