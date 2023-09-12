# airbyte-connectors-base-images

This python package contains the base images used by Airbyte connectors.
It is intended to be used as a python library.
Our connector build pipeline ([`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)) **will** use this library to build the connector images.
Our base images are declared in code, using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).



## How to get our base images
### If you're not a Dagger user:
You'll be able to get our base images from our [Docker Hub](https://hub.docker.com/u/airbyte) registry. The publish pipeline for these image is not built yet.

### If you are a Dagger user:
Install this library as a dependency of your project and import `ALL_BASE_IMAGES` from it:
```python
import dagger
from base_images import ALL_BASE_IMAGES

python_connector_base_image: dagger.Container = ALL_BASE_IMAGES["airbyte-python-connector-base:0.1.0"].container
```


## How to add a new base image version

1. `poetry install`
2. Open `base_images/python_bases.py`.
3. Declare a new class inheriting from `AirbytePythonConnectorBaseImage` or an other existing version. **The class name must follow the semver pattern `_<major>_<minor>_<patch>(AirbytePythonConnectorBaseImage)`.**
4. Implement the `container` property which must return a `dagger.Container` object.
5. Declare the `changelog` class attribute to describe the change provided by the new version.
6. *Recommended*: Override the `run_sanity_check` method to add a sanity check to your new base image version, please call the previous version sanity check to avoid breaking change: e.g `await _1_0_0.run_sanity_checks().`
7. Build the project: `poetry run build` it will run sanity checks on the images and update the changelog file.
8. Commit and push your changes.
9. Create a PR and ask for a review from the Connector Operations team.
10. Your new base image version will be available for use in the connector build pipeline once your PR is merged.

**Example: declaring a new base image version to add a system dependency (`ffmpeg`) on top of the previous version**

```python
# In base_images/python_bases.py
class _1_0_1(_1_0_0):

    changelog: str = "Add ffmpeg to the base image."

    @property
    def container(self) -> dagger.Container:        
        return (
            super()
            .container
            .with_exec(["sh", "-c", "apt-get update && apt-get install -y ffmpeg"])
        )
        

    async def run_sanity_checks(base_image_version: AirbyteConnectorBaseImage):
        await _1_0_0.run_sanity_checks(base_image_version)
        try:
            await base_image_version.container.with_exec(["ffmpeg", "-version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError("failed to run ffmpeg --version.") from e
```

## How to update an existing base image version
**Existing base image version must not be updated! Please reach out to the Connector Operations team if you have a good reason to do that.**
