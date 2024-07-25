#!/usr/bin/env bash
this_dir=$(cd $(dirname "$0"); pwd) # this script's directory
this_script=$(basename $0)

# NOTE:  -k EXPRESSION  Only run tests which match the given substring expression. An expression is a Python evaluable expression where all names are substring-matched against test names and their parent classes. Example: -k 'test_method or test_other' matches all test functions and classes whose name contains 'test_method' or 'test_other'...
poetry run pytest unit_tests "$@"
