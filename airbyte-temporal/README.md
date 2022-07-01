# airbyte-temporal

This module implements a custom version of what the Temporal autosetup image is doing. Because Temporal does not recommend the autosetup be used in production, we had to add some modifications. It ensures that the temporalDB schema will get upgraded if the temporal version is updated.

## Testing a temporal migration

`tools/bin/test_temporal_migration.sh` is available to test that a bump of the temporal version won't break the docker compose build. Here is what 
the script does:
- checkout master
- build the docker image
- run docker compose up in the background
- Sleep for 75 secondes
- shutdown docker compose
- checkout the commit being tested
- build the docker image
- run docker compose up.

At the end of the script you should be able to access a local airbyte in `localhost:8000`.

## Apple Silicon (M1) Support

Airbyte publishes an image called [airbyte/temporal-auto-setup](https://hub.docker.com/r/airbyte/temporal-auto-setup/tags) which is built for both
Intel-based and ARM-based systems.

This is because at the time of this writing, Temporal only offers their [temporalio/auto-setup](https://hub.docker.com/r/temporalio/auto-setup) image
for Intel-based (amd64) systems.

Airbyte re-publishes this image
as [airbyte/temporal-auto-setup:1.13.0-amd64](https://hub.docker.com/layers/airbyte/temporal-auto-setup/1.13.0-amd64/images/sha256-46da05b202e2fa66d9c3f5af5a31b954979d8132c4f67300e884bdad8a45b94d?context=explore)
, and also runs the `build-temporal.sh` script in this repository on an ARM-based system to build and
publish [airbyte/temporal-auto-setup:1.13.0-arm64](https://hub.docker.com/layers/airbyte/temporal-auto-setup/1.13.0-arm64/images/sha256-05027f6a9ba658205c5e961165bb8dad55c95ae0a009eddbf491d12f3d84fe20?context=explore)
.

Finally, Airbyte creates and publishes a manifest list with both images
as [airbyte/temporal-auto-setup:1.13.0](https://hub.docker.com/layers/airbyte/temporal-auto-setup/1.13.0/images/sha256-46da05b202e2fa66d9c3f5af5a31b954979d8132c4f67300e884bdad8a45b94d?context=explore)
like so:

```bash
docker manifest create airbyte/temporal-auto-setup:1.13.0 \
--amend airbyte/temporal-auto-setup:1.13.0-amd64 \
--amend airbyte/temporal-auto-setup:1.13.0-arm64
```

This process will need to be replicated for any future version upgrades beyond `1.13.0`. See the [original issue](https://github.com/airbytehq/airbyte/issues/8849) for more info.
