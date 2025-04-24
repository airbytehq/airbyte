#!/usr/bin/env bash

# Read input params
read -r -p 'Enter connector name: ' connector
read -r -p 'Enter first connector version: ' version_1
read -r -p 'Enter second connector version: ' version_2

use_state(){
  failed=false
for i in $(seq 1 3)
do read -n 1 -r -s -p "Start sync with state (y/n)?" choice
case "$choice" in
  y|Y ) failed=false ; return 1 ;;
  n|N ) failed=false ; return 0 ;;
  * ) printf "\n";;
esac
failed=true
done

if "$failed"; then
   echo "Process finished with exit code 1"
   exit 1
fi
}

use_state
if [ "$?" -eq 1 ]; then
    state_status="with"
    state="/config_files/state.json"
else
    state_status="without"
    state=""
fi

printf "\nStarting comparing connector %s version %s with version %s %s state:\n" "$connector" "$version_1" "$version_2" "$state_status"

run_docker_image()
{
  docker run --pull=missing --rm -v $(pwd)/config_files:/config_files airbyte/"$connector":"$1" read --config /config_files/secrets/config.json --catalog /config_files/configured_catalog.json --state "$state"
}

result=$( diff <(run_docker_image "$version_1") <(run_docker_image "$version_2") | grep -E 'RECORD|STATE' | sed '/\"emitted_at\"/,/}/ d')

if [ -n "$result" ]; then
    printf "%s\n" "$result"
    printf "Records output not equal."
else
    printf "Records output equal."
fi
