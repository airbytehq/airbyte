#!/bin/bash
set -e

. tools/lib/lib.sh

_python() {
  python3.7 "$@"
}

USAGE="./tools/singer/$(basename "$0") <python_venv_name> <pip_package_name> <pip_package_version> <singer_root - pass inline or as env variable SINGER_ROOT>
"

[ -z "$1" ] && echo "Venv not provided" && error "$USAGE"
[ -z "$2" ] && echo "pip package name not provided" && error "$USAGE"
[ -z "$3" ] && echo "pip package version not provided" && error "$USAGE"
[ -z "$4" ] && [[ -z $SINGER_ROOT ]] && echo "singer root not provided" && error "$USAGE"

VENV_NAME=$1 && shift
PIP_PACKAGE_NAME=$1 && shift
PIP_PACKAGE_VERSION=$1 && shift
[[ -z "$SINGER_ROOT" ]] && SINGER_ROOT=$1 && shift

echo "Creating Virutal Environment for $PIP_PACKAGE_NAME v$PIP_PACKAGE_VERSION in $SINGER_ROOT/"
cd "$SINGER_ROOT"
# Create virutal env directory
_python -m venv "$VENV_NAME"
. "$VENV_NAME/bin/activate"
_python -m pip install --upgrade pip
_python -m pip install "$PIP_PACKAGE_NAME==$PIP_PACKAGE_VERSION"
_python -m pip check && echo "No package conflicts" || exit 1
deactivate
cd -
