VERSION=$(cat .env | grep "^VERSION=" | cut -d = -f 2)

error() {
  echo "$@"
  exit 1
}

assert_root() {
  [ -f .root ] || error "Must run from root"
}

_get_docker_version() {
  local dockerfile=$1
  cat "$dockerfile" | grep io.dataline.version | cut -d = -f2
}
