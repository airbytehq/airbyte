from setuptools import setup

setup(
    name='airbyte_protocol',
    description='Contains classes representing the schema of the Airbyte protocol.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['airbyte_protocol'],
    install_requires=['PyYAML==5.3.1', 'pydantic==1.6.1']
)
