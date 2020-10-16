from setuptools import setup, find_packages

setup(
    name='source-exchangeratesapi-singer',
    description='Source implementation for the exchange rates API.',
    author='Airbyte',
    author_email='contact@airbyte.io',

    packages=find_packages(),

    install_requires=[
        'tap-exchangeratesapi==0.1.1',
        'base_singer',
        'airbyte_protocol'
    ]
)
