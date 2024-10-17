#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

#!/usr/bin/env bash

GLIDE_DOCKER_IMAGE_NAME=us-central1-docker.pkg.dev/glide-connectors/airbyte-glide-destination/destination-glide
#us-central1-docker.pkg.dev/airbyte-custom-connectors/<company>/<docker-image-name>:tag-a

GLIDE_AT_AIRBYTE_COMPANY_NAME=glide # ERROR: (gcloud.artifacts.docker.tags.list) PERMISSION_DENIED: Permission 'artifactregistry.repositories.get' denied on resource '//artifactregistry.googleapis.com/projects/airbyte-custom-connectors/locations/us-central1/repositories/glide' (or it may not exist). This command is authenticated as scott.willeke@heyglide.com which is the active account specified by the [core/account] property.
GLIDE_AT_AIRBYTE_COMPANY_NAME=heyglide 
AIRBYTE_DOCKER_IMAGE_NAME=us-central1-docker.pkg.dev/airbyte-custom-connectors/$GLIDE_AT_AIRBYTE_COMPANY_NAME/destination-glide

#echo "Pushing to remote image repository: $GLIDE_DOCKER_IMAGE_NAME"
#docker inspect --format='Pushing the local image "{{index .RepoTags 0}}" created at "{{.Created}}"' $LOCAL_BUILT_IMAGE_NAME

echo "Getting the list of tags in the airbyte cloud docker image repository:"
gcloud artifacts docker tags list $AIRBYTE_DOCKER_IMAGE_NAME


new_version=0.0.29

echo ""
echo "The new version will be $new_version and will be pushed to Airbyte's docker repo for cloud at "$AIRBYTE_DOCKER_IMAGE_NAME".  Do you want to continue? (y/n)"
read answer

if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Continuing..."
else
    echo "Exiting..."
    exit 1
fi

docker image tag $GLIDE_DOCKER_IMAGE_NAME:$new_version $AIRBYTE_DOCKER_IMAGE_NAME:$new_version
docker push $AIRBYTE_DOCKER_IMAGE_NAME:$new_version

