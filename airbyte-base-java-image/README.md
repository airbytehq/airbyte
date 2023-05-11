# Base Docker Image for Java

This Docker image provides the base for any Java-based Airbyte module.  It is currently based on the [Amazon Corretto](https://aws.amazon.com/corretto/?filtered-posts.sort-by=item.additionalFields.createdDate&filtered-posts.sort-order=desc)
distribution of [OpenJDK](https://openjdk.org/).

# Releasing

To release a new version of this base image, use the following steps:

1. Log in to [Dockerhub](https://hub.docker.com/) via the Docker CLI (`docker login`).
2. Run `docker buildx create --use` to enable Docker `buildx` if you have not used it previously.
3. Run the following to build and push a new version of this image (replace `<new_version>` with a new version!) :
   ```
   docker buildx build --push \
     --tag airbyte/airbyte-base-java-image:<new_version> \
     --platform linux/amd64,linux/arm64 .
   ```
   To see existing versions, [view the image on Dockerhub](https://hub.docker.com/r/airbyte/airbyte-base-java-image).
4. Update base Docker image tag to the new version in all Dockerfiles that depend on the base image:
   ```bash
   FROM airbyte/java-datadog-tracer-base:<NEW VERSION>
   ```

[dockerhub]: https://hub.docker.com/repository/registry-1.docker.io/airbyte/airbyte-base-java-image/general
