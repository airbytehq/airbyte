from setuptools import find_packages, setup

setup(
    name="source_langchain_sitemaploader",
    version="0.1.0",
    description="An Airbyte source connector using LangChain's SiteMapLoader.",
    author="Johann-Peter Hartmann",
    packages=find_packages(),
    install_requires=[
        "airbyte-cdk",         # adjust version as needed
        "langchain-community",         # ensure compatibility with your code
        "requests",
        "lxml",
        "fake-useragent",
        "beautifulsoup4",
    ],
    entry_points={"console_scripts": ["main=source_langchain_sitemaploader.main:main"]},
)
