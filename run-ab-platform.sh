#!/bin/bash

VERSION=0.61.0
# Run away from anything even a little scary
set -o nounset # -u exit if a variable is not set
set -o errexit # -f exit for any command failure"

# text color escape codes (please note \033 == \e but OSX doesn't respect the \e)
blue_text='\033[94m'
red_text='\033[31m'
default_text='\033[39m'

# set -x/xtrace uses a Sony PS4 for more info
PS4="$blue_text""${0}:${LINENO}: ""$default_text"

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo -e "This Script will download the necessary files for running docker compose"
   echo -e "It will also run docker compose up"
   echo -e "Take Warning! These assets may become stale over time!"
   echo
   # $0 is the currently running program
   echo -e "Syntax: $0"
   echo -e "options:"
   echo -e "   -d --download    Only download files - don't run docker compose"
   echo -e "   -r --refresh     ${red_text}DELETE${default_text} existing assets and re-download new ones"
   echo -e "   -h --help        Print this Help."
   echo -e "   -x --debug       Verbose mode."
   echo -e "   -b --background  Run docker compose up in detached mode."
   echo -e "      --dnt         Disable telemetry collection"
   echo -e ""
}

########## Declare assets care about ##########
      docker_compose_yaml="docker-compose.yaml"
docker_compose_debug_yaml="docker-compose.debug.yaml"
                  dot_env=".env"
              dot_env_dev=".env.dev"
                    flags="flags.yml"
            temporal_yaml="temporal/dynamicconfig/development.yaml"
# any string is an array to POSIX shell. Space separates values
all_files="$docker_compose_yaml $docker_compose_debug_yaml $dot_env $dot_env_dev $flags $temporal_yaml"

base_github_url="https://raw.githubusercontent.com/airbytehq/airbyte-platform/v$VERSION/"

# event states are used for telemetry data
readonly eventStateStarted="started"
readonly eventStateFailed="failed"
readonly eventStateSuccess="succeeded"

# event types are used for telemetry data
readonly eventTypeDownload="download"
readonly eventTypeInstall="install"
readonly eventTypeRefresh="refresh"

telemetrySuccess=false
telemetrySessionULID=""
telemetryUserULID=""
telemetryEnabled=true
# telemetry requires curl to be installed
if ! command -v curl > /dev/null; then
  telemetryEnabled=false
fi

# TelemetryConfig configures the telemetry variables and will disable telemetry if it cannot be configured.
TelemetryConfig()
{
  # only attempt to do anything if telemetry is not disabled
  if $telemetryEnabled; then
    telemetrySessionULID=$(curl -s http://ulid.abapp.cloud/ulid | xargs)

    if [[ $telemetrySessionULID = "" || ${#telemetrySessionULID} -ne 26 ]]; then
      # if we still don't have a ulid, give up on telemetry data
      telemetryEnabled=false
      return
    fi

    # if we have an analytics file, use it
    if test -f ~/.airbyte/analytics.yml; then
      telemetryUserULID=$(cat ~/.airbyte/analytics.yml | grep "anonymous_user_id" | cut -d ":" -f2 | xargs)
    fi
    # if the telemtery ulid is still undefined, attempt to create it and write the analytics file
    if [[ $telemetryUserULID = "" || ${#telemetryUserULID} -ne 26 ]]; then
      telemetryUserULID=$(curl -s http://ulid.abapp.cloud/ulid | xargs)
      if [[ $telemetryUserULID = "" || ${#telemetryUserULID} -ne 26 ]]; then
        # if we still don't have a ulid, give up on telemetry data
        telemetryEnabled=false
      else
        # we created a new ulid, write it out
        echo "Thanks you for using Airbyte!"
        echo "Anonymous usage reporting is currently enabled. For more information, please see https://docs.airbyte.com/telemetry"
        mkdir -p ~/.airbyte
        cat > ~/.airbyte/analytics.yml <<EOL
# This file is used by Airbyte to track anonymous usage statistics.
# For more information or to opt out, please see
# - https://docs.airbyte.com/operator-guides/telemetry
anonymous_user_id: $telemetryUserULID
EOL
      fi
    fi
  fi
}

# TelemetryDockerUp checks if the webapp container is in a running state.  If it is it will send a successful event.
# if after 20 minutes it hasn't succeeded, a failed event will be sent (or if the user terminates early, a failed event would
# also be sent).
#
# Note this only checks if the webapp container is running, that doesn't actually mean the entire stack is up.
# Some further refinement on this metric may be necessary.
TelemetryDockerUp()
{
  if ! $telemetryEnabled; then
    return
  fi

  # for up to 1200 seconds (20 minutes), check to see if the server services is in a running state
  end=$((SECONDS+1200))
  while [ $SECONDS -lt $end ]; do
    webappState=$(docker compose ps --all --format "{{.Service}}:{{.State}}" 2>/dev/null | grep server | cut -d ":" -f2 | xargs)
    if [ "$webappState" = "running" ]; then
      TelemetrySend $eventStateSuccess $eventTypeInstall
      break
    fi
    sleep 1
  done

  TelemetrySend "failed" "install" "webapp was not running within 1200 seconds"
}

readonly telemetryKey="kpYsVGLgxEqD5OuSZAQ9zWmdgBlyiaej"
readonly telemetryURL="https://api.segment.io/v1/track"
TelemetrySend()
{
  if $telemetrySuccess; then
    # due to how traps work, we don't want to send a failure for exiting docker after we sent a success
    return
  fi

  if $telemetryEnabled; then
    # start, failed, success
    local state=$1
    # install, uninstall
    local event=$2
    # optional error
    local err=${3:-""}

    local now=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
    local body=$(cat << EOL
{
  "anonymousId":"$telemetryUserULID",
  "event":"$event",
  "properties": {
    "deployment_method":"run_ab",
    "session_id":"$telemetrySessionULID",
    "state":"$state",
    "os":"$OSTYPE",
    "script_version":"$VERSION",
    "error":"$err"
  },
  "timestamp":"$now",
  "writeKey":"$telemetryKey"
}
EOL
)
    curl -s -o /dev/null -H "Content-Type: application/json" -X POST -d "$body" $telemetryURL
    if [[ $state = "success" ]]; then {
      telemetrySuccess=true
    }
    fi
  fi
}

TelemetryConfig

############################################################
# Download                                                 #
############################################################
Download()
{
  ########## Check if we already have the assets we are looking for ##########
  for file in $all_files; do
    # Account for the case where the file is in a subdirectory.
    # Make sure the directory exists to keep curl happy.
    dir_path=$(dirname "${file}")
    mkdir -p "${dir_path}"
    if test -f $file; then
      # Check if the assets are old.  A possibly sharp corner
      if test $(find $file -type f -mtime +60 > /dev/null); then
        echo -e "$red_text""Warning your $file may be stale!""$default_text"
        echo -e "$red_text""rm $file to refresh!""$default_text"
      else
        echo -e "$blue_text""found $file locally!""$default_text"
      fi
    else
      echo -e "$blue_text""Downloading $file""$default_text"
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
    echo -e "$blue_text""Attempting to delete $file!""$default_text"
    if test -f $file; then
      rm $file && echo -e "It's gone!"
    else
      echo -e "$file not found locally.  Nothing to delete."
    fi
  done
}

dockerDetachedMode=""

# $0 is the currently running program (this file)
this_file_directory=$(dirname $0)
# Run this from the / directory because we assume relative paths
cd ${this_file_directory}

args=$@
# Parse the arguments for specific flags before parsing for actions.
for argument in $args; do
  case $argument in
    -h | --help)
      Help
      exit
      ;;
    -b | --background)
      dockerDetachedMode="-d"
      ;;
    --dnt)
      telemetryEnabled=false
      ;;
  esac
done

for argument in $args; do
  case $argument in
    -d | --download)
      TelemetrySend $eventStateStarted $eventTypeDownload
      trap 'TelemetrySend $eventStateFailed $eventTypeDownload "sigint"' SIGINT
      trap 'TelemetrySend $eventStateFailed $eventTypeDownload "sigterm"' SIGTERM
      Download
      TelemetrySend $eventStateSuccess $eventTypeDownload
      exit
      ;;
    -r | --refresh)
      TelemetrySend $eventStateStarted $eventTypeRefresh
      trap 'TelemetrySend $eventStateFailed $eventTypeRefresh "sigint"' SIGINT
      trap 'TelemetrySend $eventStateFailed $eventTypeRefresh "sigterm"' SIGTERM
      DeleteLocalAssets
      Download
      TelemetrySend $eventStateSuccess $eventTypeRefresh
      exit
      ;;
    -x | --debug)
      set -o xtrace  # -x display every line before execution; enables PS4
      ;;
    -h | --help)
     # noop, this was checked in the previous for loop
      ;;
    -b | --background)
      # noop, this was checked in the previous for loop
      ;;
    --dnt)
      # noop, this was checked in the previous for loop
      ;;
    *)
      echo "$argument is not a known command."
      echo
      Help
      exit
      ;;
  esac
done

TelemetrySend $eventStateStarted $eventTypeInstall
trap 'TelemetrySend $eventStateFailed $eventTypeInstall "sigint"' SIGINT
trap 'TelemetrySend $eventStateFailed $eventTypeInstall "sigterm"' SIGTERM

########## Pointless Banner for street cred ##########
# Make sure the console is huuuge
if test $(tput cols) -ge 64; then
  # Make it green!
  echo -e "\033[32m"
  echo -e " █████╗ ██╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗"
  echo -e "██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝"
  echo -e "███████║██║██████╔╝██████╔╝ ╚████╔╝    ██║   █████╗  "
  echo -e "██╔══██║██║██╔══██╗██╔══██╗  ╚██╔╝     ██║   ██╔══╝  "
  echo -e "██║  ██║██║██║  ██║██████╔╝   ██║      ██║   ███████╗"
  echo -e "╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝    ╚═╝      ╚═╝   ╚══════╝"
  echo -e "                                            Move Data"
  # Make it less green
  echo -e "\033[0m"
  sleep 1
fi

########## Dependency Check ##########
if ! docker compose version >/dev/null 2>/dev/null; then
  echo -e "$red_text""docker compose v2 not found! please install docker compose!""$default_text"
  TelemetrySend $eventStateFailed $eventTypeInstall "docker compose not installed"
  exit 1
fi

Download

########## Source Environmental Variables ##########

for file in $dot_env $dot_env_dev; do
  echo -e "$blue_text""Loading Shell Variables from $file...""$default_text"
  source $file
done


########## Start Docker ##########
echo
echo -e "$blue_text""Starting Docker Compose""$default_text"
if [ -z "$dockerDetachedMode" ]; then
  # if running in docker-detach mode, kick off a background task as `docker compose up` will be a blocking
  # call and we'll have no way to determine when we've successfully started.
  TelemetryDockerUp &
fi

docker compose up $dockerDetachedMode

# $? is the exit code of the last command. So here: docker compose up
if test $? -ne 0; then
  echo -e "$red_text""Docker compose failed.  If you are seeing container conflicts""$default_text"
  echo -e "$red_text""please consider removing old containers""$default_text"
  TelemetrySend $eventStateFailed $eventTypeInstall "docker compose failed"
else
  TelemetrySend $eventStateSuccess $eventTypeInstall
fi

########## Ending Docker ##########
if [ -z "$dockerDetachedMode" ]; then
  docker compose down
else
  echo -e "$blue_text""Airbyte containers are running!""$default_text"
fi
