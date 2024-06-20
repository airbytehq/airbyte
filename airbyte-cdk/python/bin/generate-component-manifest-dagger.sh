#!/usr/bin/env bash

set -e

pip install dagger-io==0.9.6
python bin/generate_component_manifest_files.py