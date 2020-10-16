from setuptools import setup, find_packages

setup(
    name='template-python-source',
    description='Source implementation template',
    author='Airbyte',
    author_email='contact@airbyte.io',

    packages=find_packages(),
    package_data={
        '': ['catalog.json']
    },

    install_requires=['airbyte-protocol']
)
