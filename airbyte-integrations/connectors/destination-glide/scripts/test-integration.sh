#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

# if not GLIDE_API_KEY then print error and exit
if [ -z "$GLIDE_API_KEY" ]; then
  echo "**************************************************"
  echo "GLIDE_API_KEY is not set."
  echo "You probably want to run this like \`GLIDE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx ./${this_script}\`\n"
  exit 1
fi

poetry run pytest integration_tests "$@"
