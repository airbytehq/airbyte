#!/usr/bin/env sh

# Variables for terminal coloring
RED='\033[0;31m'
NC='\033[0m' # No Color

# The connectors folder relative path
connectors_path="../../../connectors"
# The name of the temporary folder
tmp_folder_name="tmp_output"

remove_tmp () {
  rm -rf tmp_output
  docker container rm -f airbyte-connector-bootstrap > /dev/null 2>&1
}

# This function creates the tmp folder in generator directory and copy the generated new connector to it.
# If nothing was generated or generator was stopped - this folder will be empty and removed at the enc
# After coping the generated connector from container to created tmp folder (docker cpn)
# The contains of tmp folder is looped and check each item whenever it is a directory and if the connector with
# the same name already exists in connectors folder. In this case an error msg displayed.
# Otherwise the generated connector is copied into the connectors folder.
check_and_copy_from_docker () {
  mkdir $tmp_folder_name
  docker cp airbyte-connector-bootstrap:/connectors/. $tmp_folder_name/.
  cd $tmp_folder_name || exit
  for f in *; do
    if [ -d "$f" ]; then
      if [ ! -d "$connectors_path/$f" ]; then
        cp -r "$f" "$connectors_path/$f"
      else
        >&2 echo "${RED}$f already exists in connectors. Coping aborted to prevent data overwriting${NC}"
      fi
    fi
  done
  cd ./..
}

# Remove container if already exist
remove_tmp
# Build image for container from Dockerfile
docker build . -t airbyte/connector-bootstrap
# Run the container
docker run -it  --name airbyte-connector-bootstrap -v "$(pwd)"/..:/sources airbyte/connector-bootstrap
# Copy generated template to connectors folder
check_and_copy_from_docker
# Remove container after coping files
remove_tmp

exit 0