# This function opens an ssh tunnel if required using values provided in config.
# Requires one argument,
  # path to ssh config file ($1)
function openssh() {
  # check if the ssh config file exists, it won't if ssh is off
  if [ ! -f $1 ]; then
    echo "detected no config file for ssh, assuming ssh is off."
    return 0
  fi
  # check if jq is missing, and if so try to install it..
  # this is janky but for custom dbt transform we can't be sure jq is installed as using user docker image
  if ! command -v jq &> /dev/null ; then
    echo "CRITICAL: jq not installed... attempting to install on the fly."
    { apt-get update && apt-get install -y jq; } ||
    apk --update add jq ||
    { yum install epel-release -y && yum install jq -y; } ||
    { dnf install epel-release -y && dnf install jq -y; } || return 0
  fi
  # tunnel_db_host and tunnel_db_port currently rely on the destination's spec using "host" and "port" as keys for these values
  # if adding ssh support for a new destination where this is not the case, extra logic will be needed to capture these dynamically
  tunnel_db_host=$(cat $1 | jq -r '.db_host')
  tunnel_db_port=$(cat $1 | jq -r '.db_port')
  tunnel_method=$(cat $1 | jq -r '.tunnel_map.tunnel_method' | tr '[:lower:]' '[:upper:]')
  tunnel_username=$(cat $1 | jq -r '.tunnel_map.tunnel_user')
  tunnel_host=$(cat $1 | jq -r '.tunnel_map.tunnel_host')
  tunnel_port=$(cat $1 | jq -r '.tunnel_map.tunnel_port')
  tunnel_local_port=$(cat $1 | jq -r '.local_port')
  # set a path for a control socket, allowing us to close this specific ssh connection when desired
  tmpcontrolsocket="/tmp/sshsocket${tunnel_db_remote_port}-${RANDOM}"
  if [[ ${tunnel_method} = "SSH_KEY_AUTH" ]] ; then
    echo "Detected tunnel method SSH_KEY_AUTH for normalization"
    # create a temporary file to hold ssh key and trap to delete on EXIT
    trap 'rm -f "$tmpkeyfile"' EXIT
    tmpkeyfile=$(mktemp /tmp/xyzfile.XXXXXXXXXXX) || return 1
    cat $1 | jq -r '.tunnel_map.ssh_key | gsub("\\\\n"; "\n")' > $tmpkeyfile
    # -f=background  -N=no remote command  -M=master mode  StrictHostKeyChecking=no auto-adds host
        echo "Running: ssh -f -N -M -o StrictHostKeyChecking=no -S {control socket} -i {key file} -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} -p ${tunnel_port} ${tunnel_host}"
        ssh -f -N -M -o StrictHostKeyChecking=no -S $tmpcontrolsocket -i $tmpkeyfile -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} -p ${tunnel_port} ${tunnel_host} &&
    sshopen="yes" &&
    echo "ssh tunnel opened"
    rm -f $tmpkeyfile
  elif [[ ${tunnel_method} = "SSH_PASSWORD_AUTH" ]] ; then
    echo "Detected tunnel method SSH_PASSWORD_AUTH for normalization"
    if ! command -v sshpass &> /dev/null ; then
      echo "CRITICAL: sshpass not installed... attempting to install on the fly but will fail if unable."
      { apt-get update && apt-get install -y sshpass; } ||
      { apk add --update openssh && apk --update add sshpass; } ||
      { yum install epel-release -y && yum install sshpass -y; } ||
      { dnf install epel-release -y && dnf install sshpass -y; } || return 1
    fi
    # put ssh password in env var for use in sshpass. Better than directly passing with -p
    export SSHPASS=$(cat $1 | jq -r '.tunnel_map.tunnel_user_password')
    echo "Running: sshpass -e ssh -f -N -M -o StrictHostKeyChecking=no -S {control socket} -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} -p ${tunnel_port} ${tunnel_host}"
    sshpass -e ssh -f -N -M -o StrictHostKeyChecking=no -S $tmpcontrolsocket -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} -p ${tunnel_port} ${tunnel_host} &&
    sshopen="yes" &&
    echo "ssh tunnel opened"
  fi
}

# This function checks if $sshopen variable has been set and if so, closes the ssh open via $tmpcontrolsocket
# This only works after calling openssh()
function closessh() {
  # $sshopen $tmpcontrolsocket comes from openssh() function
  if [ ! -z "$sshopen" ] ; then
    ssh -S $tmpcontrolsocket -O exit -p ${tunnel_port} ${tunnel_host} &&
    echo "closed ssh tunnel"
    trap 'rm -f "$tmpcontrolsocket"' EXIT
  fi
}
