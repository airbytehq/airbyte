"""Setup for the source-comfyui Airbyte connector."""

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.80.0",
    "requests",
]

TEST_REQUIREMENTS = [
    "pytest",
    "pytest-mock",
    "requests-mock",
]

setup(
    name="source_comfyui",
    version="0.1.0",
    description="Airbyte source connector for ComfyUI Cloud API.",
    author="3act",
    author_email="vincent.lange@3act.ai",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={"dev": TEST_REQUIREMENTS},
    package_data={"source_comfyui": ["spec.yaml", "schemas/*.json"]},
    entry_points={
        "console_scripts": [
            "source-comfyui=source_comfyui.__main__:main",
        ],
    },
)
