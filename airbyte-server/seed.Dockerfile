FROM alpine:3.4 AS seed

WORKDIR /app

# the sole purpose of this image is to seed the data volume with the default data
# that the app should have when it is first installed.
COPY build/config_init/resources/main/config seed/config