from setuptools import setup

setup(
    name='google_sheets_source',
    description='Source implementation for Google Sheets.',
    author='Airbyte',
    author_email='contact@airbyte.io',
    packages=['google_sheets_source'],
    install_requires=[
        'requests',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'base_singer',
        'airbyte_protocol']
)

