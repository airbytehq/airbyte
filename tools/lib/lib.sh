error() {
  echo -e "$@"
  exit 1
}

assert_root() {
  [ -f .root ] || error "Must run from root"
}

_script_directory() {
  local base; base=$(dirname $0)

  [ -z "$base" ] && base="."
  (cd "$base" && pwd)
}

_get_docker_label() {
  local dockerfile; dockerfile=$1
  local label; label=$2

  < "$dockerfile" grep "$label" | cut -d = -f2
}

_get_docker_image_version() {
  _get_docker_label $1 io.airbyte.version
}

_get_docker_image_name() {
  _get_docker_label $1 io.airbyte.name
}

_to_gradle_path() {
  local path=$1
  local task=$2

  echo ":$(echo "$path" | tr -s / :):${task}"
}

full_path_to_gradle_path() {
  # converts any Airbyte repo path to gradle job
  local path="$1/$2"
  python -c "print(':airbyte-' + ':'.join(p for p in '${path}'.split('airbyte-')[-1].replace('/', ':').split(':') if p))"
}

VERSION=$(cat .env | grep "^VERSION=" | cut -d = -f 2); export VERSION
SCRIPT_DIRECTORY=$(_script_directory); export SCRIPT_DIRECTORY
