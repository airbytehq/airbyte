/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.util.CompressionTypeHelper.parseCompressionType
import io.airbyte.commons.json.Jsons.jsonNode
import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class CompressionTypeHelperTest {
    @Test
    fun testGetCompressionType() {
        Assertions.assertEquals(
            S3DestinationConstants.DEFAULT_COMPRESSION_TYPE,
            parseCompressionType(null)
        )

        Assertions.assertEquals(
            CompressionType.NO_COMPRESSION,
            parseCompressionType(jsonNode(Map.of("compression_type", "No Compression")))
        )

        Assertions.assertEquals(
            CompressionType.GZIP,
            parseCompressionType(jsonNode(Map.of("compression_type", "GZIP")))
        )
    }
}
