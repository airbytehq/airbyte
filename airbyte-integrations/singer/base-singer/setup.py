from setuptools import setup

setup(
    name='base-singer',
    description='Contains helpers for handling Singer sources and destinations.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['base_singer'],
    install_requires=['airbyte-protocol']
)
