#!/usr/bin/env bash

set -e
set -x

. tools/lib/lib.sh

USAGE="
Usage: $(basename "$0") <cmd>
For publish, if you want to push the spec to the spec cache, provide a path to a service account key file that can write to the cache.
Available commands:
  scaffold
  build  <integration_root_path> [<run_tests>]
  publish  <integration_root_path> [<run_tests>] [--publish_spec_to_cache] [--publish_spec_to_cache_with_key_file <path to keyfile>]
  publish_external  <image_name> <image_version>
"

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
  ./gradlew --no-daemon "$(_to_gradle_path "$path" clean)"
  ./gradlew --no-daemon "$(_to_gradle_path "$path" build)"

  if [ "$run_tests" = false ] ; then
    echo "Skipping integration tests..."
  else
    echo "Running integration tests..."
    ./gradlew --no-daemon "$(_to_gradle_path "$path" integrationTest)"
  fi
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
  local latest_image=$image_name:latest

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
    VERSION=$image_version GIT_REVISION=$GIT_REVISION docker-compose -f airbyte-integrations/bases/base-normalization/docker-compose.build.yaml build
    VERSION=$image_version GIT_REVISION=$GIT_REVISION docker-compose -f airbyte-integrations/bases/base-normalization/docker-compose.build.yaml push
    VERSION=latest         GIT_REVISION=$GIT_REVISION docker-compose -f airbyte-integrations/bases/base-normalization/docker-compose.build.yaml build
    VERSION=latest         GIT_REVISION=$GIT_REVISION docker-compose -f airbyte-integrations/bases/base-normalization/docker-compose.build.yaml push
  else
    docker tag "$image_name:dev" "$versioned_image"
    docker tag "$image_name:dev" "$latest_image"

    echo "Publishing new version ($versioned_image)"
    docker push "$versioned_image"
    docker push "$latest_image"
  fi

  if [[ "true" == "${publish_spec_to_cache}" ]]; then
    echo "Publishing and writing to spec cache."

    # publish spec to cache. do so, by running get spec locally and then pushing it to gcs.
    local tmp_spec_file; tmp_spec_file=$(mktemp)
    docker run --rm "$versioned_image" spec | \
      # 1. filter out any lines that are not valid json.
      jq -R "fromjson? | ." | \
      # 2. grab any json that has a spec in it.
      # 3. if there are more than one, take the first one.
      # 4. if there are none, throw an error.
      jq -s "map(select(.spec != null)) | map(.spec) | first | if . != null then . else error(\"no spec found\") end" \
      > "$tmp_spec_file"

    # use service account key file is provided.
    if [[ -n "${spec_cache_writer_sa_key_file}" ]]; then
      echo "Using provided service account key"
      gcloud auth activate-service-account --key-file "$spec_cache_writer_sa_key_file"
    else
      echo "Using environment gcloud"
    fi

    gsutil cp "$tmp_spec_file" gs://io-airbyte-cloud-spec-cache/specs/"$image_name"/"$image_version"/spec.json
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
  # publish spec to cache. do so, by running get spec locally and then pushing it to gcs.
  local tmp_spec_file; tmp_spec_file=$(mktemp)
  docker run --rm "$image_name:$image_version" spec | \
    # 1. filter out any lines that are not valid json.
    jq -R "fromjson? | ." | \
    # 2. grab any json that has a spec in it.
    # 3. if there are more than one, take the first one.
    # 4. if there are none, throw an error.
    jq -s "map(select(.spec != null)) | map(.spec) | first | if . != null then . else error(\"no spec found\") end" \
    > "$tmp_spec_file"

  echo "Using environment gcloud"

  gsutil cp "$tmp_spec_file" gs://io-airbyte-cloud-spec-cache/specs/"$image_name"/"$image_version"/spec.json
}

main() {
  assert_root

  local cmd=$1; shift || error "Missing cmd $USAGE"
  cmd_"$cmd" "$@"
}

main "$@"
