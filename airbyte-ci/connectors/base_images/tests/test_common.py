#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from base_images import common, consts


class TestPlatformAwareDockerImage:
    def test_get_full_image_name(self):
        image = common.PlatformAwareDockerImage(
            image_name="my-image",
            tag="v1.0",
            sha="abc123",
            platform=consts.SUPPORTED_PLATFORMS[0],
        )

        expected_full_image_name = "my-image:v1.0@sha256:abc123"

        full_image_name = image.get_full_image_name()

        assert full_image_name == expected_full_image_name
