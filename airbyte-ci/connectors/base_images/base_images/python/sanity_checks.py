#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dagger

from base_images import errors
from base_images import sanity_checks as base_sanity_checks


async def check_python_version(container: dagger.Container, expected_python_version: str):
    """Checks that the python version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_python_version (str): The expected python version.

    Raises:
        errors.SanityCheckError: Raised if the python --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        python_version_output: str = await container.with_exec(["python", "--version"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if python_version_output != f"Python {expected_python_version}\n":
        raise errors.SanityCheckError(f"unexpected python version: {python_version_output}")


async def check_pip_version(container: dagger.Container, expected_pip_version: str):
    """Checks that the pip version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_pip_version (str): The expected pip version.

    Raises:
        errors.SanityCheckError: Raised if the pip --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        pip_version_output: str = await container.with_exec(["pip", "--version"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if not pip_version_output.startswith(f"pip {expected_pip_version}"):
        raise errors.SanityCheckError(f"unexpected pip version: {pip_version_output}")


async def check_poetry_version(container: dagger.Container, expected_poetry_version: str):
    """Checks that the poetry version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_poetry_version (str): The expected poetry version.

    Raises:
        errors.SanityCheckError: Raised if the poetry --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        poetry_version_output: str = await container.with_exec(["poetry", "--version"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if not poetry_version_output.startswith(f"Poetry (version {expected_poetry_version}"):
        raise errors.SanityCheckError(f"unexpected poetry version: {poetry_version_output}")


async def check_python_image_has_expected_env_vars(python_image_container: dagger.Container):
    """Check a python container has the set of env var we always expect on python images.

    Args:
        python_image_container (dagger.Container): The container on which the sanity checks should run.
    """
    expected_env_vars = {
        "PYTHON_VERSION",
        "HOME",
        "PATH",
        "LANG",
        "GPG_KEY",
    }
    # It's not suboptimal to call printenv multiple times because the printenv output is cached.
    for expected_env_var in expected_env_vars:
        await base_sanity_checks.check_env_var_with_printenv(python_image_container, expected_env_var)


async def check_nltk_data(python_image_container: dagger.Container):
    """Install nltk and check that the required data is available.
    As of today the required data is:
    - taggers/averaged_perceptron_tagger
    - tokenizers/punkt

    Args:
        python_image_container (dagger.Container): The container on which the sanity checks should run.

    Raises:
        errors.SanityCheckError: Raised if the nltk data is not available.
    """
    with_nltk = await python_image_container.with_exec(["pip", "install", "nltk==3.8.1"])
    try:
        await with_nltk.with_exec(
            ["python", "-c", 'import nltk;nltk.data.find("taggers/averaged_perceptron_tagger");nltk.data.find("tokenizers/punkt")']
        )
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)


async def check_tesseract_version(python_image_container: dagger.Container, tesseract_version: str):
    """Check that the tesseract version is the expected one.

    Args:
        python_image_container (dagger.Container): The container on which the sanity checks should run.
        tesseract_version (str): The expected tesseract version.

    Raises:
        errors.SanityCheckError: Raised if the tesseract --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        tesseract_version_output = await python_image_container.with_exec(["tesseract", "--version"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if not tesseract_version_output.startswith(f"tesseract {tesseract_version}"):
        raise errors.SanityCheckError(f"unexpected tesseract version: {tesseract_version_output}")


async def check_poppler_utils_version(python_image_container: dagger.Container, poppler_version: str):
    """Check that the poppler version is the expected one.
    The poppler version can be checked by running a pdftotext -v command.

    Args:
        python_image_container (dagger.Container): The container on which the sanity checks should run.
        poppler_version (str): The expected poppler version.

    Raises:
        errors.SanityCheckError: Raised if the pdftotext -v command could not be executed or if the outputted version is not the expected one.
    """
    try:
        pdf_to_text_version_output = await python_image_container.with_exec(["pdftotext", "-v"]).stderr()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)

    if f"pdftotext version {poppler_version}" not in pdf_to_text_version_output:
        raise errors.SanityCheckError(f"unexpected poppler version: {pdf_to_text_version_output}")


async def check_cdk_system_dependencies(python_image_container: dagger.Container):
    await check_nltk_data(python_image_container)
    await check_tesseract_version(python_image_container, "5.3.0")
    await check_poppler_utils_version(python_image_container, "22.12.0")
