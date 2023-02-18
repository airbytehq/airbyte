# Run away from anything even a little scary
set -o nounset # -u exit if a variable is not set
set -o errexit # -f exit for any command failure


# text color escape codes (please note \033 == \e but OSX doesn't respect the \e)
blue_text='\033[94m'
red_text='\033[31m'
default_text='\033[39m'

# set -x/xtrace uses a Sony PS4 for more info
PS4="$blue_text""${BASH_SOURCE}:${LINENO}: ""$default_text"

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Add description of the script functions here."
   echo
   echo "Syntax: run-ab-platform.sh [-d|x|h]"
   echo "options:"
   echo "d     Only download files - don't run docker compose"
   echo "h     Print this Help."
   echo "x     Verbose mode."
   echo
}

############################################################
# Download                                                 #
############################################################
Download()
{
  ########## Check if we already have the assets we are looking for ##########
  docker_compose_yaml="docker-compose.yaml"
              dot_env=".env"
          dot_env_dev=".env.dev"
                flags="flags.yml"
  base_github_url="https://raw.githubusercontent.com/airbytehq/airbyte-platform/main/"
  # url_to_docker_compose_yaml="${base_github_url}${docker_compose_yaml}"
  # url_to_dot_env="${base_github_url}${dot_env}"
  # url_to_dot_env_dev="${base_github_url}${dot_env_dev}"

  for file in $docker_compose_yaml $dot_env $dot_env_dev $flags; do
    if test $(find $file -type f -mtime +15 > /dev/null); then
      echo "$red_text""Warning your $file may be stale!""$default_text"
      echo "$red_text""rm $file to refresh!""$default_text"
    fi
    if test -f $file; then
      echo "$blue_text""found $file locally!""$default_text"
    else
      echo "$blue_text""Downloading $file""$default_text"
      curl --location\
        --fail\
        --silent\
        --show-error \
        ${base_github_url}${file} > $file
    fi
  done
}


# $0 is the currently running program (this file)
this_file_directory=$(dirname $0)
# Run this from the / directory because we assume relative paths
cd ${this_file_directory}



while getopts dhx flag
do
    case "${flag}" in
        d) 
          Download
          exit
          ;;
        h)       
          Help
          exit
          ;;
        x) 
          set -o xtrace  # -x display every line before execution; enables PS4
          ;;
    esac
done


########## Pointless Banner for street cred ##########
# Make sure the console is huuuge
if test $(tput cols) -ge 64; then
  # Make it green!
  echo "\033[32m"
  echo " █████╗ ██╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗"
  echo "██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝"
  echo "███████║██║██████╔╝██████╔╝ ╚████╔╝    ██║   █████╗  "
  echo "██╔══██║██║██╔══██╗██╔══██╗  ╚██╔╝     ██║   ██╔══╝  "
  echo "██║  ██║██║██║  ██║██████╔╝   ██║      ██║   ███████╗"
  echo "╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝    ╚═╝      ╚═╝   ╚══════╝"
  echo "                                            Move Data"
  # Make it less green
  echo "\033[0m"
  sleep 1
fi

########## Dependency Check ##########
if ! which -s docker-compose; then
  echo "$red_text""docker compose not found! please install docker compose!""$default_text"
fi

Download

########## Source Envionmental Variables ##########

for file in $dot_env $dot_env_dev; do
  echo "$blue_text""Loading Shell Variables from $file...""$default_text"
  source $file
done


########## Start Docker ##########

echo
echo "$blue_text""Starting Docker Compose""$default_text"

docker-compose up

if test $? -ne 0; then
  echo "$red_text""Docker compose failed.  If you are seeing container conflicts""$default_text"
  echo "$red_text""please consider removing old containers""$default_text"
fi

########## Ending Docker ##########

docker-compose down

