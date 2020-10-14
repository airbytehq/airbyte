from setuptools import setup

setup(
    name='source_stripe_singer',
    description='Source implementation for Stripe.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['source_stripe_singer'],
    install_requires=[
        'tap-stripe==1.4.4',
        'requests',
        'base_singer',
        'airbyte_protocol']
)

