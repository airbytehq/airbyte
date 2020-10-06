from setuptools import setup

setup(
    name='source_exchangeratesapi_singer',
    description='Source implementation for the exchange rates API.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['source_exchangeratesapi_singer'],
    install_requires=['tap-exchangeratesapi==0.1.1', 'base_singer', 'airbyte_protocol']
)
