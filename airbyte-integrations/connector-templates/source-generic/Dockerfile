FROM scratch

## TODO Add your dockerfile instructions here
## TODO uncomment the below line. This is required for Kubernetes compatibility.
# ENV AIRBYTE_ENTRYPOINT="update this with the command you use for an entrypoint"

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-{{dashCase name}}
LABEL io.airbyte.version=0.1.0
