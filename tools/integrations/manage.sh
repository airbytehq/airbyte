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
"

_check_tag_exists() {
  DOCKER_CLI_EXPERIMENTAL=enabled docker manifest inspect "$1" > /dev/null
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

  cmd_build "$path" "$run_tests"

  local image_name; image_name=$(_get_docker_image_name "$path"/Dockerfile)
  local image_version; image_version=$(_get_docker_image_version "$path"/Dockerfile)
  local versioned_image=$image_name:$image_version
  local latest_image=$image_name:latest

  echo "image_name $image_name"
  echo "$versioned_image $versioned_image"
  echo "latest_image $latest_image"

  docker tag "$image_name:dev" "$versioned_image"
  docker tag "$image_name:dev" "$latest_image"

  if _check_tag_exists "$versioned_image"; then
    error "You're trying to push a version that was already released ($versioned_image). Make sure you bump it up."
  fi

  echo "Publishing new version ($versioned_image)"
  docker push "$versioned_image"
  docker push "$latest_image"

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

main() {
  assert_root

  local cmd=$1; shift || error "Missing cmd $USAGE"
  cmd_"$cmd" "$@"
}

main "$@"
