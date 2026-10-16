/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.command.ValidatedJsonUtils
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class S3BucketSpecificationTest {

    @Test
    fun `defaults to path style`() {
        assertEquals(
            S3AddressingStyle.PATH_STYLE,
            defaultSpecification().toS3BucketConfiguration().s3AddressingStyle,
        )
    }

    @Test
    fun `null addressing style falls back to path style`() {
        assertEquals(
            S3AddressingStyle.PATH_STYLE,
            specification(null).toS3BucketConfiguration().s3AddressingStyle,
        )
    }

    @Test
    fun `maps explicit virtual hosted style`() {
        assertEquals(
            S3AddressingStyle.VIRTUAL_HOSTED_STYLE,
            specification(S3AddressingStyle.VIRTUAL_HOSTED_STYLE)
                .toS3BucketConfiguration()
                .s3AddressingStyle,
        )
    }

    @Test
    fun `serializes addressing styles as configuration values`() {
        val objectMapper = ObjectMapper()

        assertEquals(
            "\"path_style\"",
            objectMapper.writeValueAsString(S3AddressingStyle.PATH_STYLE)
        )
        assertEquals(
            "\"virtual_hosted_style\"",
            objectMapper.writeValueAsString(S3AddressingStyle.VIRTUAL_HOSTED_STYLE),
        )
    }

    @Test
    fun `existing specifications do not expose the addressing style`() {
        val properties =
            ValidatedJsonUtils.generateAirbyteJsonSchema(LegacyBucketSpecification::class.java)
                .get("properties")

        assertFalse(properties.has("s3AddressingStyle"))
        assertFalse(properties.has("s3_addressing_style"))
    }

    private fun defaultSpecification(): S3BucketSpecification = LegacyBucketSpecification()

    private fun specification(addressingStyle: S3AddressingStyle?): S3BucketSpecification =
        object : S3BucketSpecification {
            override val s3BucketName = "bucket"
            override val s3BucketRegion = S3BucketRegion.`us-east-1`
            override val s3Endpoint = "https://s3.example.com"
            override val s3AddressingStyle = addressingStyle
        }

    class LegacyBucketSpecification : S3BucketSpecification {
        override val s3BucketName = "bucket"
        override val s3BucketRegion = S3BucketRegion.`us-east-1`
        override val s3Endpoint = "https://s3.example.com"
    }
}
