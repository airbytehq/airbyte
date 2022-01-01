#!/usr/bin/env bash

set -e

# Ensure always run from this directory because uses relative paths
cd "$(dirname "${0}")" || exit 1

scversion="v$(cat ../../.shellcheck-version)"
wget -qO- "https://github.com/koalaman/shellcheck/releases/download/${scversion?}/shellcheck-${scversion?}.linux.x86_64.tar.xz" | tar -xJv
sudo cp "shellcheck-${scversion}/shellcheck" /usr/bin/

# If the above does not work for you, you can install via: https://github.com/koalaman/shellcheck#installing

shellcheck --version
