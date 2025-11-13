# Parse the command-line args that we care about.
# Scripts sourcing this script can be invoked as either:
# ./foo.sh [--release-type=<pre-release|main-release>] [--publish] [--name=<source/destination-foo>]* [--name <source/destination-foo>]*
# Or, if invoked with no `--name` flags:
# ./get-modified-connectors.sh --json | ./foo.sh [--release-type=<pre-release|main-release>] [--publish]
publish_mode="pre-release"
do_publish=false
connectors=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      sed -n '1,34p' "$0"
      exit 0
      ;;
    --release-type=*)
      publish_mode="${1#*=}"
      shift
      ;;
    --release-type)
      publish_mode="$2"
      shift 2
      ;;
    --publish)
      do_publish=true
      shift
      ;;
    --name=*)
      connectors+=("${1#*=}")
      shift
      ;;
    --name)
      connectors+=("$2")
      shift 2
      ;;
    --*)
      echo "Error: Unknown flag $1" >&2
      exit 1
      ;;
    *)
      connectors+=("$1")
      shift
      ;;
  esac
done
