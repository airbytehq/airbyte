# Copyright (C) 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import find_packages
from setuptools import setup

setup(
    name='stevedore-examples2',
    version='1.0',

    description='Demonstration package for stevedore',

    author='Doug Hellmann',
    author_email='doug@doughellmann.com',

    url='http://opendev.org/openstack/stevedore',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=['stevedore.examples2',
              ],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'stevedore.example.formatter': [
            'field = stevedore.example2.fields:FieldList',
        ],
    },

    zip_safe=False,
)
