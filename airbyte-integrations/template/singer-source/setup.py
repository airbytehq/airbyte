from setuptools import setup, find_packages

setup(
    name='template-singer-source',
    description='Singer source implementation template',
    author='Airbyte',
    author_email='contact@airbyte.io',

    packages=find_packages(),

    install_requires=[
        'tap-exchangeratesapi==0.1.1',
        'base_singer',
        'airbyte_protocol'
    ]
)
