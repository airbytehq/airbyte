import setuptools

setuptools.setup(
    name='airbyte-protocol',
    description='Contains classes representing the schema of the Airbyte protocol.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    url='https://github.com/airbytehq/airbyte',

    packages=setuptools.find_packages(),
    package_data={
        '': ['models/yaml/*.yaml']
    },

    install_requires=[
        'PyYAML==5.3.1',
        'python-jsonschema-objects==0.3.13'
    ],
    entry_points={
        'console_scripts': [
            'base-python=airbyte_protocol.entrypoint:main'
        ],
    }
)
