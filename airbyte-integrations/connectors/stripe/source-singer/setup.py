from setuptools import setup, find_packages

setup(
    name='source_stripe_singer',
    description='Source implementation for Stripe.',
    author='Airbyte',
    author_email='contact@airbyte.io',

    packages=find_packages(),
    package_data={
        '': ['*.json']
    },

    install_requires=[
        'tap-stripe==1.4.4',
        'requests',
        'base_singer',
        'airbyte_protocol'
    ]
)
