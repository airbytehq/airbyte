#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

# So... it looks like when the airbyte-ci builds the multi-architecture images, it puts each one on a different tag locally.
# We should probably push amd64 only or at least make it the "default" and make arm tagged sepraately. 
# if we built and pushed all at once we could have a single tag for both architectures. However, we're using the airbyte-ci to build and that makes pushing a separate step.
# It looks like there is experimental support for using docker manfiest to combine tags into a single multi-arch image at https://docs.docker.com/reference/cli/docker/manifest/
LOCAL_BUILT_IMAGE_TAG_AMD64=dev-linux-amd64
LOCAL_BUILT_IMAGE_TAG_ARM64=dev-linux-arm64

LOCAL_BUILT_IMAGE_NAME=airbyte/destination-glide
# GLIDE_DOCKER_IMAGE_NAME is really only useful if we want to use it entirely in Airbyte OSS. To use in Airbyte cloud we *must* push to the airbyte-managed repo.
#GLIDE_DOCKER_IMAGE_NAME=us-central1-docker.pkg.dev/glide-connectors/airbyte-glide-destination/destination-glide

# AIRBYTE_DOCKER_IMAGE_NAME is the repo we use for Airbyte's Cloud instance.
GLIDE_AT_AIRBYTE_COMPANY_NAME=heyglide 
AIRBYTE_DOCKER_IMAGE_NAME=us-central1-docker.pkg.dev/airbyte-custom-connectors/$GLIDE_AT_AIRBYTE_COMPANY_NAME/destination-glide

echo "Will push to remote image repository: $AIRBYTE_DOCKER_IMAGE_NAME"

docker inspect --format='Pushing the local image "{{index .RepoTags 0}}" created at "{{.Created}}"' $LOCAL_BUILT_IMAGE_NAME:$LOCAL_BUILT_IMAGE_TAG_AMD64
if [ $? -ne 0 ]; then
    echo "Error: The local image $LOCAL_BUILT_IMAGE_NAME does not exist.  Please build the image first."
    exit 1
fi

# Fetch the list of tags from Docker Hub
#tags=$(wget -q -O - "https://hub.docker.com/v2/namespaces/activescott/repositories/destination-glide/tags?page_size=10" | grep -o '"name": *"[^"]*' | grep -o '[^"]*$' | grep -E '([0-9]+\.)+[0-9]+' )
# Get the list of tags using gcloud with the appropriate format
tags=$(gcloud artifacts docker tags list $AIRBYTE_DOCKER_IMAGE_NAME --format="get(tag)")

# Sort the tags and get the highest one
highest_tag=$(echo "$tags" | awk -F'/' '{print $NF}' | sed 's/latest//g' | sort -V | tail -n 1)

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

docker image tag $LOCAL_BUILT_IMAGE_NAME:$LOCAL_BUILT_IMAGE_TAG_AMD64 $AIRBYTE_DOCKER_IMAGE_NAME:$new_version
if [ $? -ne 0 ]; then
    echo "Error: The local image $LOCAL_BUILT_IMAGE_NAME does not exist.  Please build the image first."
    exit 1
fi

# Push the image with the new tag
docker push $AIRBYTE_DOCKER_IMAGE_NAME:$new_version
if [ $? -ne 0 ]; then
    echo "Error: The local image $LOCAL_BUILT_IMAGE_NAME does not exist.  Please build the image first."
    exit 1
fi

echo "Do you want to make this new version the 'latest' tag in Docker too (so that new pulls get this version by default)? (y/n)"
read answer

if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Taging latest..."
    docker image tag $AIRBYTE_DOCKER_IMAGE_NAME:$new_version $AIRBYTE_DOCKER_IMAGE_NAME:latest
    docker push $AIRBYTE_DOCKER_IMAGE_NAME:latest
else
    echo "Exiting..."
    exit 0
fi
