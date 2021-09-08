# This function opens an ssh tunnel if required using values provided in config.
# Requires two arguments,
  # path to config file ($1)
  # path to file containing local port to use ($2)
function openssh() {
  # check if jq is missing, and if so try to install it..
  # this is janky but for custom dbt transform we can't be sure jq is installed as using user docker image
  if ! command -v jq &> /dev/null ; then
    echo "CRITICAL: jq not installed... attempting to install on the fly but will fail if unable."
    { apt-get update && apt-get install -y jq; } ||
    apk --update add jq ||
    { yum install epel-release -y && yum install jq -y; } ||
    { dnf install epel-release -y && dnf install jq -y; } || exit 1
  fi
  # tunnel_db_host and tunnel_db_port currently rely on the destination's spec using "host" and "port" as keys for these values
  # if adding ssh support for a new destination where this is not the case, extra logic will be needed to capture these dynamically
  tunnel_db_host=$(cat $1 | jq -r '.host')
  tunnel_db_port=$(cat $1 | jq -r '.port')
  tunnel_method=$(cat $1 | jq -r '.tunnel_method.tunnel_method' | tr '[:lower:]' '[:upper:]')
  tunnel_username=$(cat $1 | jq -r '.tunnel_method.tunnel_user')
  tunnel_host=$(cat $1 | jq -r '.tunnel_method.tunnel_host')
  tunnel_local_port=$(cat $2 | jq -r '.port')
  # set a path for a control socket, allowing us to close this specific ssh connection when desired
  tmpcontrolsocket="/tmp/sshsocket${tunnel_db_remote_port}-${RANDOM}"
  if [[ ${tunnel_method} = "SSH_KEY_AUTH" ]] ; then
    echo "Detected tunnel method SSH_KEY_AUTH for normalization"
    # create a temporary file to hold ssh key and trap to delete on EXIT
    trap 'rm -f "$tmpkeyfile"' EXIT
    tmpkeyfile=$(mktemp /tmp/xyzfile.XXXXXXXXXXX) || exit 1
    echo "$(cat $1 | jq -r '.tunnel_method.ssh_key')" > $tmpkeyfile
    # -f=background  -N=no remote command  -M=master mode  StrictHostKeyChecking=no auto-adds host
    echo "Running: ssh -f -N -M -o StrictHostKeyChecking=no -S {control socket} -i {key file} -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} ${tunnel_host}"
    ssh -f -N -M -o StrictHostKeyChecking=no -S $tmpcontrolsocket -i $tmpkeyfile -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} ${tunnel_host} &&
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
      { dnf install epel-release -y && dnf install sshpass -y; } || exit 1
    fi
    # put ssh password in env var for use in sshpass. Better than directly passing with -p
    export SSHPASS=$(cat $1 | jq -r '.tunnel_method.tunnel_user_password')
    echo "Running: sshpass -e ssh -f -N -M -o StrictHostKeyChecking=no -S {control socket} -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} ${tunnel_host}"
    sshpass -e ssh -f -N -M -o StrictHostKeyChecking=no -S $tmpcontrolsocket -l ${tunnel_username} -L ${tunnel_local_port}:${tunnel_db_host}:${tunnel_db_port} ${tunnel_host} &&
    sshopen="yes" &&
    echo "ssh tunnel opened"
  fi
}

# This function checks if $sshopen variable has been set and if so, closes the ssh open via $tmpcontrolsocket
# This only works after calling openssh()
function closessh() {
  # $sshopen $tmpcontrolsocket comes from openssh() function
  if [ ! -z "$sshopen" ] ; then
    ssh -S $tmpcontrolsocket -O exit ${tunnel_host} &&
    echo "closed ssh tunnel"
    trap 'rm -f "$tmpcontrolsocket"' EXIT
  fi
}
