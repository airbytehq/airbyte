#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

#!/usr/bin/env bash
LOCAL_BUILT_IMAGE_NAME=airbyte/destination-glide:dev
GLIDE_DOCKER_IMAGE_NAME=us-central1-docker.pkg.dev/glide-connectors/airbyte-glide-destination/destination-glide

echo "Pushing to remote image repository: $GLIDE_DOCKER_IMAGE_NAME"
docker inspect --format='Pushing the local image "{{index .RepoTags 0}}" created at "{{.Created}}"' $LOCAL_BUILT_IMAGE_NAME


# Fetch the list of tags from Docker Hub
#tags=$(wget -q -O - "https://hub.docker.com/v2/namespaces/activescott/repositories/destination-glide/tags?page_size=10" | grep -o '"name": *"[^"]*' | grep -o '[^"]*$' | grep -E '([0-9]+\.)+[0-9]+' )
# Get the list of tags using gcloud with the appropriate format
tags=$(gcloud artifacts docker tags list $GLIDE_DOCKER_IMAGE_NAME --format="get(tag)")

# Sort the tags and get the highest one
highest_tag=$(echo "$tags" | awk -F'/' '{print $NF}' | sort -V | tail -n 1)

echo "found highest tag on remote: $highest_tag"

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
# NOTE: airbyte/destination-glide is the local docker image that airbyte's CI builds and names locally.

docker image tag $LOCAL_BUILT_IMAGE_NAME $GLIDE_DOCKER_IMAGE_NAME:$new_version

# Push the image with the new tag
docker push $GLIDE_DOCKER_IMAGE_NAME:$new_version

echo "Do you want to make this new version the 'latest' tag in Docker too (so that new pulls get this version by default)? (y/n)"
read answer

if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Taging latest..."
    docker image tag $LOCAL_BUILT_IMAGE_NAME $GLIDE_DOCKER_IMAGE_NAME:latest
    docker push $GLIDE_DOCKER_IMAGE_NAME:latest
else
    echo "Exiting..."
    exit 0
fi
