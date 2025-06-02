from setuptools import setup

setup(
    name='source-sap-hana',
    version='0.1.0',
    install_requires=[
        'hdbcli',
    ],
    packages=['source_sap_hana'],
)
