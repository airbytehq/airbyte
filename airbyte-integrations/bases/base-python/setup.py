# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="base-python",
    version="0.0.1",
    description="Contains machinery to make it easy to write an integration in python.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Airbyte",
    author_email="contact@airbyte.io",
    license="MIT",
    url="https://github.com/airbytehq/airbyte",
    packages=find_packages(exclude=("tests",)),
    package_data={"": ["models/yaml/*.yaml"]},
    install_requires=[
        "PyYAML==5.4",
        "pydantic==1.6.1",
        "airbyte-protocol",
        "jsonschema==2.6.0",
        "requests",
        "backoff",
        "pytest",
        "pendulum",
    ],
    entry_points={
        "console_scripts": ["base-python=base_python.entrypoint:main"],
    },
)
