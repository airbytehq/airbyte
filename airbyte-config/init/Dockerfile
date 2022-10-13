ARG ALPINE_IMAGE=alpine:3.13
FROM ${ALPINE_IMAGE} AS seed

WORKDIR /app

# the sole purpose of this image is to seed the data volume with the default data
# that the app should have when it is first installed.
COPY bin/scripts scripts
