#!/bin/bash
pip install setuptools wheel
pip install twine
python3 airbyte-cdk/python/setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
