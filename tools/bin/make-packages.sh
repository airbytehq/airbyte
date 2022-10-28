#!/bin/bash
set -e

###
#
# NOTE: to generate a list of all the packages in the connectors directory, I can use: `find /Users/michaelsiega/airbyte/airbyte-integrations | grep setup.py | grep -v ".venv" | while read arg; do dirname $arg | sed 's#.*/##'; done | sort`
#
###

########################################
#                                      #
# === Make the directory structure === #
#                                      #
########################################
package_name="$1";
pypi_token="$2";
echo "Generating a package for ${package_name}...";
mkdir "${package_name}";
mkdir "${package_name}/src";
mkdir "${package_name}/tests";
mkdir "${package_name}/src/${package_name}";



##########################
#                        #
# === Make the files === #
#                        #
##########################
cat << EOF > "${package_name}/LICENSE"
Copyright (c) 2018 The Python Packaging Authority

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

cat << EOF > "${package_name}/README.md"
# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
EOF

cat << EOF > "${package_name}/pyproject.toml"
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "${package_name}"
version = "1.0.0"
authors = [
  { name="Example Author", email="author@example.com" },
]
description = "A small example package"
readme = "README.md"
requires-python = ">=3.7"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/pypa/sampleproject"
"Bug Tracker" = "https://github.com/pypa/sampleproject/issues"
EOF

touch "${package_name}/src/__init__.py"

########################################
#                                      #
# === Build and upload the package === #
#                                      #
########################################

cp ./.pypirc "./${package_name}" && cd "${package_name}" && python3 -m build && python3 -m twine upload dist/* && cd ..
# cd "${package_name}" && python3 -m build && cd ..
echo "Generated ${package_name}."
