/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BlobDecoratorTest {
    @Test
    fun testOverwriteMetadata() {
        val metadata: MutableMap<String, String> = HashMap()
        metadata["amz-foo"] = "oldValue"

        BlobDecorator.insertMetadata(metadata, Map.of("foo", "amz-foo"), "foo", "newValue")

        Assertions.assertEquals(Map.of("amz-foo", "newValue"), metadata)
    }

    @Test
    fun testNewMetadata() {
        val metadata: MutableMap<String, String> = HashMap()
        metadata["amz-foo"] = "oldValue"

        BlobDecorator.insertMetadata(metadata, Map.of("bar", "amz-bar"), "bar", "newValue")

        Assertions.assertEquals(Map.of("amz-foo", "oldValue", "amz-bar", "newValue"), metadata)
    }

    @Test
    fun testSkipMetadata() {
        val metadata: MutableMap<String, String> = HashMap()
        metadata["amz-foo"] = "oldValue"

        BlobDecorator.insertMetadata(metadata, Map.of("foo", "amz-foo"), "bar", "newValue")

        Assertions.assertEquals(Map.of("amz-foo", "oldValue"), metadata)
    }
}
