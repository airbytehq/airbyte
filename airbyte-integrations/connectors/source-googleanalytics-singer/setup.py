"""
MIT License

Copyright (c) 2020 Airbyte

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
"""

from setuptools import find_packages, setup

setup(
    name="googleanalytics-singer-source",
    description="Airbyte Source for Google Analytics (singer-based)",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    package_data={"": ["*.json", "*.txt"]},
    # two sets of dependencies: 1) for main 2) for standard test deps. 2 does not have all of the dependencies of 1, which is we cannot use install_requires.
    extras_require={
        "main": [
            "pipelinewise-tap-google-analytics==1.1.1",
            "pydantic==1.6.1",
            "base-singer",
            "airbyte-protocol",
        ],
        "standardtest": ["airbyte-python-test", "requests"],
    },
)
