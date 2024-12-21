/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DestinationRecordAirbyteValueToAirbyteValueWithMetaTest {
    val stream = MockDestinationCatalogFactory.stream1
    val emittedAtMs = 123456L
    val syncId = stream.syncId
    val generationId = stream.generationId
    val expectedMeta =
        linkedMapOf(
            // Don't do raw_id, we'll evict it and validate that it's a uuid
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(emittedAtMs),
            Meta.COLUMN_NAME_AB_META to
                ObjectValue(
                    linkedMapOf(
                        "sync_id" to IntegerValue(syncId),
                        "changes" to ArrayValue(emptyList())
                    )
                ),
            Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(generationId)
        )

    @Test
    fun testWithoutFlattening() {
        val data =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("John"),
                    "age" to IntegerValue(30),
                    "is_cool" to BooleanValue(true)
                )
            )
        val expected = LinkedHashMap(expectedMeta)
        expected[Meta.COLUMN_NAME_DATA] = data
        val mockRecord = DestinationRecordAirbyteValue(stream.descriptor, data, emittedAtMs, Meta())
        val withMeta = mockRecord.dataWithAirbyteMeta(stream, flatten = false)
        val uuid = withMeta.values.remove(Meta.COLUMN_NAME_AB_RAW_ID) as StringValue
        Assertions.assertTrue(
            uuid.value.matches(
                Regex("[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")
            )
        )
        Assertions.assertEquals(expected, withMeta.values)
    }

    @Test
    fun testWithFlattening() {
        val data =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("John"),
                    "age" to IntegerValue(30),
                    "is_cool" to BooleanValue(true)
                )
            )
        val expected = LinkedHashMap(expectedMeta)
        data.values.forEach { (name, value) -> expected[name] = value }
        val mockRecord = DestinationRecordAirbyteValue(stream.descriptor, data, emittedAtMs, Meta())
        val withMeta = mockRecord.dataWithAirbyteMeta(stream, flatten = true)
        withMeta.values.remove(Meta.COLUMN_NAME_AB_RAW_ID)
        Assertions.assertEquals(expected, withMeta.values)
    }
}
