#!/usr/bin/env sh
CWD=$(pwd)
cd ../../bases/source-acceptance-test
pip install -e .
python -m pytest --acceptance-test-config=${CWD} "$@"
