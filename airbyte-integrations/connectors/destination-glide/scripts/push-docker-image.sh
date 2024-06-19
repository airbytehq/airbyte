#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

#!/usr/bin/env bash

# Fetch the list of tags from Docker Hub
tags=$(wget -q -O - "https://hub.docker.com/v2/namespaces/activescott/repositories/destination-glide/tags?page_size=10" | grep -o '"name": *"[^"]*' | grep -o '[^"]*$' | grep -E '([0-9]+\.)+[0-9]+' )
``
echo "Found tags: $tags"
# Sort the tags and get the highest one
highest_tag=$(echo "$tags" | sort -V | tail -n 1)

echo "found highest tag: $highest_tag"

# Increment the version
IFS='.' read -ra ADDR <<< "$highest_tag"
new_version="${ADDR[0]}.${ADDR[1]}.$((ADDR[2]+1))"

# Show the user the new version and ask if they want to continue
echo "The new version will be $new_version. Do you want to continue? (y/n)"
read answer

if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Continuing..."
else
    echo "Exiting..."
    exit 1
fi


# Tag the local image with the new version
# TODO: airbyte/destination-glide is the local docker image that airbyte's CI builds it and names it as locally. Can't we change this ??
docker image tag airbyte/destination-glide:dev activescott/destination-glide:$new_version

# Push the image with the new tag
docker push activescott/destination-glide:$new_version


