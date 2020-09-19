This docker image contains the build environment used to generate all our artifacts.

If you need to do some changes the environment:
1. Bump up the version in the docker file (`io.airbyte.version`).
1. Build and push the image (with the new tag).
1. Update the consumers to use the most recent build image.
