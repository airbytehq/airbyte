#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

./gradlew --no-daemon --scan -x generateProtocolClassFiles \
  :airbyte-integrations:connectors:source-github-singer:standardSourceTestPython \
  :airbyte-integrations:connectors:source-marketo-singer:standardSourceTestPython
