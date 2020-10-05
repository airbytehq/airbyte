from setuptools import setup

setup(
    name='source_implementation',
    description='Source implementation for the exchange rates API.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['source_implementation'],
    install_requires=["tap-exchangeratesapi==0.1.1"]
)
