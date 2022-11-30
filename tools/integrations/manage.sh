#!/usr/bin/env bash

set -e
set -x

. tools/lib/lib.sh

USAGE="
Usage: $(basename "$0") <cmd>
For publish, if you want to push the spec to the spec cache, provide a path to a service account key file that can write to the cache.
Available commands:
  scaffold
  test <integration_root_path>
  build  <integration_root_path> [<run_tests>]
  publish  <integration_root_path> [<run_tests>] [--publish_spec_to_cache] [--publish_spec_to_cache_with_key_file <path to keyfile>]
  publish_external  <image_name> <image_version>
"

# these filenames must match DEFAULT_SPEC_FILE and CLOUD_SPEC_FILE in GcsBucketSpecFetcher.java
default_spec_file="spec.json"
cloud_spec_file="spec.cloud.json"

_check_tag_exists() {
  DOCKER_CLI_EXPERIMENTAL=enabled docker manifest inspect "$1" > /dev/null
}

_error_if_tag_exists() {
    if _check_tag_exists "$1"; then
      error "You're trying to push a version that was already released ($1). Make sure you bump it up."
    fi
}

cmd_scaffold() {
  echo "Scaffolding connector"
  (
    cd airbyte-integrations/connector-templates/generator &&
    ./generate.sh "$@"
  )
}

cmd_build() {
  local path=$1; shift || error "Missing target (root path of integration) $USAGE"
  [ -d "$path" ] || error "Path must be the root path of the integration"

  local run_tests=$1; shift || run_tests=true

  echo "Building $path"
  # Note that we are only building (and testing) once on this build machine's architecture
  # Learn more @ https://github.com/airbytehq/airbyte/pull/13004
  ./gradlew --no-daemon "$(_to_gradle_path "$path" clean)"

  if [ "$run_tests" = false ] ; then
    echo "Building and skipping unit tests + integration tests..."
    ./gradlew --no-daemon "$(_to_gradle_path "$path" build)" -x test
  else
    echo "Building and running unit tests + integration tests..."
    ./gradlew --no-daemon "$(_to_gradle_path "$path" build)"

    if test "$path" == "airbyte-integrations/bases/base-normalization"; then
      ./gradlew --no-daemon --scan :airbyte-integrations:bases:base-normalization:airbyteDocker
    fi

    ./gradlew --no-daemon "$(_to_gradle_path "$path" integrationTest)"
  fi
}

# Experimental version of the above for a new way to build/tag images
cmd_build_experiment() {
  local path=$1; shift || error "Missing target (root path of integration) $USAGE"
  [ -d "$path" ] || error "Path must be the root path of the integration"

  echo "Building $path"
  ./gradlew --no-daemon "$(_to_gradle_path "$path" clean)"
  ./gradlew --no-daemon "$(_to_gradle_path "$path" build)"

  # After this happens this image should exist: "image_name:dev"
  # Re-tag with CI candidate label
  local image_name; image_name=$(_get_docker_image_name "$path/Dockerfile")
  local image_version; image_version=$(_get_docker_image_version "$path/Dockerfile")
  local image_candidate_tag; image_candidate_tag="$image_version-candidate-$PR_NUMBER"

  # If running via the bump-build-test-connector job, re-tag gradle built image following candidate image pattern
  if [[ "$GITHUB_JOB" == "bump-build-test-connector" ]]; then
    docker tag "$image_name:dev" "$image_name:$image_candidate_tag"
    # TODO: docker push "$image_name:$image_candidate_tag"
  fi
}

cmd_test() {
  local path=$1; shift || error "Missing target (root path of integration) $USAGE"
  [ -d "$path" ] || error "Path must be the root path of the integration"

  # TODO: needs to know to use alternate image tag from cmd_build_experiment
  echo "Running integration tests..."
  ./gradlew --no-daemon "$(_to_gradle_path "$path" integrationTest)"
}

# Bumps connector version in Dockerfile, definitions.yaml file, and updates seeds with gradle.
# This does not build or test, it solely manages the versions of connectors to be +1'd.
#
# NOTE: this does NOT update changelogs because the changelog markdown files do not have a reliable machine-readable
# format to automatically handle this. Someday it could though: https://github.com/airbytehq/airbyte/issues/12031
cmd_bump_version() {
  # Take params
  local connector_path
  local bump_version
  connector_path="$1" # Should look like airbyte-integrations/connectors/source-X
  bump_version="$2" || bump_version="patch"

  # Set local constants
  connector=${connector_path#airbyte-integrations/connectors/}
  if [[ "$connector" =~ "source-" ]]; then
    connector_type="source"
  elif [[ "$connector" =~ "destination-" ]]; then
    connector_type="destination"
  else
    echo "Invalid connector_type from $connector"
    exit 1
  fi
  definitions_path="./airbyte-config/init/src/main/resources/seed/${connector_type}_definitions.yaml"
  dockerfile="$connector_path/Dockerfile"
  master_dockerfile="/tmp/master_${connector}_dockerfile"
  # This allows getting the contents of a file without checking it out
  git --no-pager show "origin/master:$dockerfile" > "$master_dockerfile"

  # Current version always comes from master, this way we can always bump correctly relative to master
  # verses a potentially stale local branch
  current_version=$(_get_docker_image_version "$master_dockerfile")
  local image_name; image_name=$(_get_docker_image_name "$dockerfile")
  rm "$master_dockerfile"

  ## Create bumped version
  IFS=. read -r major_version minor_version patch_version <<<"${current_version##*-}"
  case "$bump_version" in
    "major")
      ((major_version++))
      minor_version=0
      patch_version=0
      ;;
    "minor")
      ((minor_version++))
      patch_version=0
      ;;
    "patch")
      ((patch_version++))
      ;;
    *)
      echo "Invalid bump_version option: $bump_version. Valid options are major, minor, patch"
      exit 1
  esac

  bumped_version="$major_version.$minor_version.$patch_version"
  # This image should not already exist, if it does, something weird happened
  _error_if_tag_exists "$image_name:$bumped_version"
  echo "$connector:$current_version will be bumped to $connector:$bumped_version"

  ## Write new version to files
  # 1) Dockerfile
  sed -i "s/$current_version/$bumped_version/g" "$dockerfile"

  # 2) Definitions YAML file
  definitions_check=$(yq e ".. | select(has(\"dockerRepository\")) | select(.dockerRepository == \"$connector\")" "$definitions_path")

  if [[ (-z "$definitions_check") ]]; then
    echo "Could not find $connector in $definitions_path, exiting 1"
    exit 1
  fi

  connector_name=$(yq e ".[] | select(has(\"dockerRepository\")) | select(.dockerRepository == \"$connector\") | .name" "$definitions_path")
  yq e "(.[] | select(.name == \"$connector_name\").dockerImageTag)|=\"$bumped_version\"" -i "$definitions_path"

  # 3) Seed files
  ./gradlew :airbyte-config:init:processResources

  echo "Woohoo! Successfully bumped $connector:$current_version to $connector:$bumped_version"
}

cmd_publish() {
  local path=$1; shift || error "Missing target (root path of integration) $USAGE"
  [ -d "$path" ] || error "Path must be the root path of the integration"

  local run_tests=$1; shift || run_tests=true
  local publish_spec_to_cache
  local spec_cache_writer_sa_key_file

  while [ $# -ne 0 ]; do
    case "$1" in
    --publish_spec_to_cache)
      publish_spec_to_cache=true
      shift 1
      ;;
    --publish_spec_to_cache_with_key_file)
      publish_spec_to_cache=true
      spec_cache_writer_sa_key_file="$2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
    esac
  done

  if [[ ! $path =~ "connectors" ]]
  then
     # Do not publish spec to cache in case this is not a connector
     publish_spec_to_cache=false
  fi

  # setting local variables for docker image versioning
  local image_name; image_name=$(_get_docker_image_name "$path"/Dockerfile)
  local image_version; image_version=$(_get_docker_image_version "$path"/Dockerfile)
  local versioned_image=$image_name:$image_version
  local latest_image="$image_name" # don't include ":latest", that's assumed here
  local build_arch="linux/amd64,linux/arm64"

  # learn about this version of Docker
  echo "--- docker info ---"
  docker --version
  docker buildx version

  # Install docker emulators
  # TODO: Don't run this command on M1 macs locally (it won't work and isn't needed)
  apt-get update && apt-get install -y qemu-user-static

  # log into docker
  if test -z "${DOCKER_HUB_USERNAME}"; then
    echo 'DOCKER_HUB_USERNAME not set.';
    exit 1;
  fi

  if test -z "${DOCKER_HUB_PASSWORD}"; then
    echo 'DOCKER_HUB_PASSWORD for docker user not set.';
    exit 1;
  fi

  set +x
  DOCKER_TOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"username": "'${DOCKER_HUB_USERNAME}'", "password": "'${DOCKER_HUB_PASSWORD}'"}' https://hub.docker.com/v2/users/login/ | jq -r .token)
  set -x

  echo "image_name $image_name"
  echo "versioned_image $versioned_image"
  echo "latest_image $latest_image"

  # before we start working sanity check that this version has not been published yet, so that we do not spend a lot of
  # time building, running tests to realize this version is a duplicate.
  _error_if_tag_exists "$versioned_image"

  # building the connector
  cmd_build "$path" "$run_tests"

  # in case curing the build / tests someone this version has been published.
  _error_if_tag_exists "$versioned_image"

  if [[ "airbyte/normalization" == "${image_name}" ]]; then
    echo "Publishing normalization images (version: $versioned_image)"
    GIT_REVISION=$(git rev-parse HEAD)

    # We use a buildx docker container when building multi-stage builds from one docker compose file
    # This works because all the images depend only on already public images
    docker buildx create --name connector-buildx --driver docker-container --use

    # Note: "buildx bake" needs to be run within the directory
    local original_pwd=$PWD
    cd airbyte-integrations/bases/base-normalization

    VERSION=$image_version GIT_REVISION=$GIT_REVISION docker buildx bake \
      --set "*.platform=$build_arch"                                     \
      -f docker-compose.build.yaml                                       \
      --push

    VERSION=latest GIT_REVISION=$GIT_REVISION docker buildx bake \
      --set "*.platform=$build_arch"                             \
      -f docker-compose.build.yaml                               \
      --push

    docker buildx rm connector-buildx

    cd $original_pwd
  else
    # We have to go arch-by-arch locally (see https://github.com/docker/buildx/issues/59 for more info) due to our base images (e.g. airbyte-integrations/bases/base-java)
    # Alternative local approach @ https://github.com/docker/buildx/issues/301#issuecomment-755164475
    # We need to use the regular docker buildx driver (not docker container) because we need this intermediate contaiers to be available for later build steps

    for arch in $(echo $build_arch | sed "s/,/ /g")
    do
      echo "building base images for $arch"
      docker buildx build -t airbyte/integration-base:dev --platform $arch --load airbyte-integrations/bases/base
      docker buildx build -t airbyte/integration-base-java:dev --platform $arch --load airbyte-integrations/bases/base-java

      local arch_versioned_image=$image_name:`echo $arch | sed "s/\//-/g"`-$image_version
      echo "Publishing new version ($arch_versioned_image) from $path"
      docker buildx build -t $arch_versioned_image --platform $arch --push $path
      docker manifest create $latest_image --amend $arch_versioned_image
      docker manifest create $versioned_image --amend $arch_versioned_image
    done

    docker manifest push $latest_image
    docker manifest push $versioned_image
    docker manifest rm $latest_image
    docker manifest rm $versioned_image

    # delete the temporary image tags made with arch_versioned_image
    sleep 10
    for arch in $(echo $build_arch | sed "s/,/ /g")
    do
      local arch_versioned_tag=`echo $arch | sed "s/\//-/g"`-$image_version
      echo "deleting temporary tag: ${image_name}/tags/${arch_versioned_tag}"
      TAG_URL="https://hub.docker.com/v2/repositories/${image_name}/tags/${arch_versioned_tag}/" # trailing slash is needed!
      set +x
      curl -X DELETE -H "Authorization: JWT ${DOCKER_TOKEN}" "$TAG_URL"
      set -x
    done

  fi

  # Checking if the image was successfully registered on DockerHub
  # see the description of this PR to understand why this is needed https://github.com/airbytehq/airbyte/pull/11654/
  sleep 5

  # To work for private repos we need a token as well
  TAG_URL="https://hub.docker.com/v2/repositories/${image_name}/tags/${image_version}"
  set +x
  DOCKERHUB_RESPONSE_CODE=$(curl --silent --output /dev/null --write-out "%{http_code}" -H "Authorization: JWT ${DOCKER_TOKEN}" ${TAG_URL})
  set -x
  if [[ "${DOCKERHUB_RESPONSE_CODE}" == "404" ]]; then
    echo "Tag ${image_version} was not registered on DockerHub for image ${image_name}, please try to bump the version again." && exit 1
  fi

  if [[ "true" == "${publish_spec_to_cache}" ]]; then
    echo "Publishing and writing to spec cache."

    # use service account key file is provided.
    if [[ -n "${spec_cache_writer_sa_key_file}" ]]; then
      echo "Using provided service account key"
      gcloud auth activate-service-account --key-file "$spec_cache_writer_sa_key_file"
    else
      echo "Using environment gcloud"
    fi

    publish_spec_files "$image_name" "$image_version"
  else
    echo "Publishing without writing to spec cache."
  fi
}

cmd_publish_external() {
  local image_name=$1; shift || error "Missing target (image name) $USAGE"
  # Get version from the command
  local image_version=$1; shift || error "Missing target (image version) $USAGE"

  echo "image $image_name:$image_version"
  echo "Publishing and writing to spec cache."
  echo "Using environment gcloud"

  publish_spec_files "$image_name" "$image_version"
}

generate_spec_file() {
  local image_name=$1; shift || error "Missing target (image name)"
  local image_version=$1; shift || error "Missing target (image version)"
  local tmp_spec_file=$1; shift || error "Missing target (temp spec file name)"
  local deployment_mode=$1; shift || error "Missing target (deployment mode)"

  docker run --env DEPLOYMENT_MODE="$deployment_mode" --rm "$image_name:$image_version" spec | \
      # 1. filter out any lines that are not valid json.
      jq -R "fromjson? | ." | \
      # 2. grab any json that has a spec in it.
      # 3. if there are more than one, take the first one.
      # 4. if there are none, throw an error.
      jq -s "map(select(.spec != null)) | map(.spec) | first | if . != null then . else error(\"no spec found\") end" \
      > "$tmp_spec_file"
}

publish_spec_files() {
  local image_name=$1; shift || error "Missing target (image name)"
  local image_version=$1; shift || error "Missing target (image version)"

  # publish spec to cache. do so, by running get spec locally and then pushing it to gcs.
  local tmp_default_spec_file; tmp_default_spec_file=$(mktemp)
  local tmp_cloud_spec_file; tmp_cloud_spec_file=$(mktemp)

  # generate oss and cloud spec files
  generate_spec_file "$image_name" "$image_version" "$tmp_default_spec_file" "OSS"
  generate_spec_file "$image_name" "$image_version" "$tmp_cloud_spec_file" "CLOUD"

  gsutil cp "$tmp_default_spec_file" "gs://io-airbyte-cloud-spec-cache/specs/$image_name/$image_version/$default_spec_file"
  if cmp --silent -- "$tmp_default_spec_file" "$tmp_cloud_spec_file"; then
    echo "This connector has the same spec file for OSS and cloud"
  else
    echo "Uploading cloud specific spec file"
    gsutil cp "$tmp_cloud_spec_file" "gs://io-airbyte-cloud-spec-cache/specs/$image_name/$image_version/$cloud_spec_file"
  fi
}

main() {
  assert_root

  local cmd=$1; shift || error "Missing cmd $USAGE"
  cmd_"$cmd" "$@"
}

main "$@"
