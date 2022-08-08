#!/bin/bash
set +e
pip install setuptools wheel
pip install twine
cd airbyte-cdk/python
rm -r dist
python3 setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
rm -r dist
cd ../..
