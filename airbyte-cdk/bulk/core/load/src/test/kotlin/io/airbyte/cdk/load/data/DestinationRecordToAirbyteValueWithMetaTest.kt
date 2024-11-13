/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.message.DestinationRecord
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DestinationRecordToAirbyteValueWithMetaTest {
    val stream = MockDestinationCatalogFactory.stream1
    val emittedAtMs = 123456L
    val syncId = stream.syncId
    val generationId = stream.generationId
    val expectedMeta =
        linkedMapOf(
            // Don't do raw_id, we'll evict it and validate that it's a uuid
            DestinationRecord.Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(emittedAtMs),
            DestinationRecord.Meta.COLUMN_NAME_AB_META to
                ObjectValue(
                    linkedMapOf(
                        "sync_id" to IntegerValue(syncId),
                        "changes" to ArrayValue(emptyList())
                    )
                ),
            DestinationRecord.Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(generationId)
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
        expected[DestinationRecord.Meta.COLUMN_NAME_DATA] = data
        val mockRecord =
            DestinationRecord(
                stream.descriptor,
                data,
                emittedAtMs,
                DestinationRecord.Meta(),
                "dummy"
            )
        val withMeta = mockRecord.dataWithAirbyteMeta(stream, flatten = false)
        val uuid =
            withMeta.values.remove(DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID) as StringValue
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
        val mockRecord =
            DestinationRecord(
                stream.descriptor,
                data,
                emittedAtMs,
                DestinationRecord.Meta(),
                "dummy"
            )
        val withMeta = mockRecord.dataWithAirbyteMeta(stream, flatten = true)
        withMeta.values.remove(DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID)
        Assertions.assertEquals(expected, withMeta.values)
    }
}
