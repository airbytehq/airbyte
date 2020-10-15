FROM alpine:3.4 AS seed

WORKDIR /app

# the sole purpose of this image is to seed the data volume with the default data
# that the app should have when it is first installed.
COPY create_mount_directories.sh create_mount_directories.sh
COPY copy_seed_data.sh copy_seed_data.sh
COPY src/main/resources/config seed/config
