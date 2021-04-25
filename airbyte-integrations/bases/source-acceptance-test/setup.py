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


import setuptools

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "docker==4.4.4",
    "PyYAML==5.3.1",
    "inflection==0.5.1",
    "icdiff==1.9.1",
    "pendulum==1.2.0",
    "pydantic==1.6.1",
    "pytest==6.1.2",
    "pytest-timeout==1.4.2",
    "pprintpp==0.4.0",
]

setuptools.setup(
    name="source-acceptance-test",
    description="Contains classes for running integration tests.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    entry_points={"pytest11": ["pytest-airbyte = source_acceptance_test.plugin"]},
)
