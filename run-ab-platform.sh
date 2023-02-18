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
   echo "This Script will download the necessary files for running docker compose"
   echo "It will also run docker compose up"
   echo "Take Warning! These assets may become stale over time!"
   echo
   # $0 is the currently running program
   echo "Syntax: $0"
   echo "options:"
   echo "   -d --download    Only download files - don't run docker compose"
   echo "   -r --refresh     ${red_text}DELETE${default_text} existing assets and re-download new ones"
   echo "   -h --help        Print this Help."
   echo "   -x --debug       Verbose mode."
   echo
}

########## Declare assets care about ##########
docker_compose_yaml="docker-compose.yaml"
            dot_env=".env"
        dot_env_dev=".env.dev"
              flags="flags.yml"
# any string is an array to POSIX shell. Space seperates values
all_files="$docker_compose_yaml $dot_env $dot_env_dev $flags"
base_github_url="https://raw.githubusercontent.com/airbytehq/airbyte-platform/main/"

############################################################
# Download                                                 #
############################################################
Download()
{
  ########## Check if we already have the assets we are looking for ##########
  for file in $all_files; do
    if test -f $file; then
      # Check if the assets are old.  A possibly sharp corner
      if test $(find $file -type f -mtime +60 > /dev/null); then
        echo "$red_text""Warning your $file may be stale!""$default_text"
        echo "$red_text""rm $file to refresh!""$default_text"
      else
        echo "$blue_text""found $file locally!""$default_text"
      fi
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

DeleteLocalAssets()
{
  for file in $all_files; do
    echo "$blue_text""Attempting to delete $file!""$default_text"
    if test -f $file; then
      rm $file && echo "It's gone!"
    else
      echo "$file not found locally.  Nothing to delete."
    fi
  done
}


# $0 is the currently running program (this file)
this_file_directory=$(dirname $0)
# Run this from the / directory because we assume relative paths
cd ${this_file_directory}


for argument in $@; do
  case $argument in
    -d | --download)
      Download
      exit
      ;;
    -r | --refresh)
      DeleteLocalAssets
      exit
      ;;
    -h | --help)
      Help
      exit
      ;;
    -x | --debug)
      set -o xtrace  # -x display every line before execution; enables PS4
      ;;
    *)
      echo "$argument is not a known command."
      echo
      Help
      exit
      ;;
  esac
  shift
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

# $? is the exit code of the last command. So here: docker-compose up
if test $? -ne 0; then
  echo "$red_text""Docker compose failed.  If you are seeing container conflicts""$default_text"
  echo "$red_text""please consider removing old containers""$default_text"
fi

########## Ending Docker ##########
docker-compose down

echo "$blue_text""Starting Docker Compose""$default_text"
