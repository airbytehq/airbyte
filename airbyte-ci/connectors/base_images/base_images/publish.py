#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import dagger

from base_images import bases, consts, published_image


async def run_sanity_checks(base_image_version: bases.AirbyteConnectorBaseImage):
    for platform in consts.PLATFORMS_WE_PUBLISH_FOR:
        await base_image_version.run_sanity_checks(platform)


async def publish_to_remote_registry(base_image_version: bases.AirbyteConnectorBaseImage) -> published_image.PublishedImage:
    """Publishes a base image to the remote registry.

    Args:
        base_image_version (common.AirbyteConnectorBaseImage): The base image to publish.

    Returns:
        models.PublishedImage: The published image as a PublishedImage instance.
    """

    address = f"{consts.REMOTE_REGISTRY}/{base_image_version.repository}:{base_image_version.version}"
    variants_to_publish = []
    for platform in consts.PLATFORMS_WE_PUBLISH_FOR:
        await base_image_version.run_sanity_checks(platform)
        variants_to_publish.append(base_image_version.get_container(platform))
    # Publish with forced compression to ensure backward compatibility with older versions of docker
    published_address = await variants_to_publish[0].publish(
        address, platform_variants=variants_to_publish[1:], forced_compression=dagger.ImageLayerCompression.Gzip
    )
    return published_image.PublishedImage.from_address(published_address)
