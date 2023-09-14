# airbyte-connectors-base-images

This python package contains the base images used by Airbyte connectors.
It is intended to be used as a python library.
Our connector build pipeline ([`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)) **will** use this library to build the connector images.
Our base images are declared in code, using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).

## Base images changelog
The base changelog files are automatically generated and updated by the build pipeline.
* [airbyte-python-connector-base changelog]("https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/generated/docs/base_images_changelog/airbyte-python-connector-base.md")


## Where are the Dockerfiles?
Our base images are not declared using Dockerfiles.
They are declared in code using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).
We prefer this approach because it allows us to interact with base images container as code: we can use python to declare the base images and use the full power of the language to build and test them.
However, we do artificially generate Dockerfiles for debugging and documentation purposes.
Feel free to check the `generated/dockerfiles` directory.


## How to get our base images
### If you're not a Dagger user:
You'll be able to get our base images from our [Docker Hub](https://hub.docker.com/u/airbyte) registry. The publish pipeline for these image is not built yet.

### If you are a Dagger user:
Install this library as a dependency of your project and import `GLOBAL_REGISTRY` from it:
```python
import platform

import anyio
import dagger

# You must have this library installed in your project
from base_images import GLOBAL_REGISTRY

CURRENT_PLATFORM = dagger.Platform(f"linux/{platform.machine()}")
BaseImageVersion = GLOBAL_REGISTRY.get_version("airbyte-python-connector-base:0.1.0")

async def main():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        python_connector_base_container: dagger.Container = BaseImageVersion(dagger_client, CURRENT_PLATFORM).container
        # Do something with the container
        python_version_output: str = await python_connector_base_container.with_exec(["python", "--version"]).stdout()
        print(python_version_output)

anyio.run(main)
```


## How to add a new base image version

0. Please install the repo pre-commit hook: from airbyte repo root run `pre-commit install`. It will make sure that the changelog file is up to date and committed on changes.
1. `poetry install`
2. Open the latest version module: e.g `base_images/python/v1.py`.
3. Declare a new class inheriting from `AirbytePythonConnectorBaseImage` or an other existing version. **The class name must follow the semver pattern `_<major>_<minor>_<patch>(AirbytePythonConnectorBaseImage)`.**
4. Implement the `container` property which must return a `dagger.Container` object.
5. Declare the `changelog` class attribute to describe the change provided by the new version.
6. *Recommended*: Override the `run_sanity_check` method to add a sanity check to your new base image version
7. To detect regressions you can set the run_previous_version_sanity_checks attribute to True .`
8. Build the project: `poetry run build` it will run sanity checks on the images, generate dockerfiles and update the changelog file.
9. If you face any issue, feel free to run `LOG_LEVEL=DEBUG poetry run build` to get access to the full logs.
10. Commit and push your changes.
11. Create a PR and ask for a review from the Connector Operations team.
12. Your new base image version will be available for use in the connector build pipeline once your PR is merged.

**Example: declaring a new base image version to add a system dependency (`ffmpeg`) on top of the previous version**

```python
# In base_images/python/v1.py

from base_images import sanity_checks, python

# We enforce direct inheritance from AirbytePythonConnectorBaseImage
class _1_0_1(python.AirbytePythonConnectorBaseImage):

    base_base_image: Final[PythonBase] = PythonBase.PYTHON_3_9_18

    changelog: str = "Add ffmpeg to the base image."
    
    # This will run the previous version sanity checks on top of the new version.
    # This is helpful to detect regressions.
    run_previous_version_sanity_checks = True

    @property
    def container(self) -> dagger.Container:
        # We encourage declarative programming here to facilitate the maintenance of the base images.
        # To prevent refactoring side effects we'd love this container property to be idempotent and not call any external code except the base_container and Dagger API.
        pip_cache_volume: dagger.CacheVolume = self.dagger_client.cache_volume(AirbytePythonConnectorBaseImage.pip_cache_name)
      
        return (
            self.base_container.with_mounted_cache("/root/.cache/pip", pip_cache_volume)
            # Set the timezone to UTC
            .with_exec(["ln", "-snf", "/usr/share/zoneinfo/Etc/UTC", "/etc/localtime"])
            # Upgrade pip to the expected version
            .with_exec(["pip", "install", "--upgrade", "pip==23.2.1"])
            # Install ffmpeg
            .with_exec(["sh", "-c", "apt-get update && apt-get install -y ffmpeg"])
        )
        

    async def run_sanity_checks(base_image_version: AirbyteConnectorBaseImage):
        try:
            # Feel free to add additional re-usable sanity checks in the sanity_checks module.
            await sanity_checks.check_a_command_is_available_using_version_option(
                base_image_version.container, 
                "ffmpeg"
            )
```

## How to update an existing base image version
**Existing base image version must not be updated or deleted! Please reach out to the Connector Operations team if you have a good reason to do that.**

## Running tests locally
```bash
poetry run pytest
# Static typing checks
poetry run mypy base_images --check-untyped-defs
```

