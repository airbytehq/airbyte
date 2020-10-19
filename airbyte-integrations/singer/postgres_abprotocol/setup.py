from setuptools import setup, find_packages

setup(
    name='postgres-singer-source',
    description='Postgres Singer source',
    author='Airbyte',
    author_email='contact@airbyte.io',

    packages=find_packages(),
    package_data={
        '': ['*.json']
    },

    install_requires=[
        'psycopg2==2.7.4',
        'tap-postgres==0.1.0',
        'base_singer',
        'airbyte_protocol'
    ]
)
