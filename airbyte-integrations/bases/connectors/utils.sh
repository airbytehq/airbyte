die () {
  echo "$1" 1>&2
  exit 1
}

docker_build_quiet () {
  [ -n "$1" ] || die "Missing TAG"
  local TAG="$1"
  docker build -t "$TAG" -q .
}
