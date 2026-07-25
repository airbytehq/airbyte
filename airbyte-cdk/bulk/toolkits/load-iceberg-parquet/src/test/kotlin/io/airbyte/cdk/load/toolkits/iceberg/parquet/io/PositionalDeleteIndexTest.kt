/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import kotlin.test.assertEquals
import kotlin.test.assertNull
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Test

internal class PositionalDeleteIndexTest {
    private val keySchema =
        Schema(
            Types.NestedField.required(1, "id", Types.IntegerType.get()),
            Types.NestedField.required(2, "tenant", Types.StringType.get()),
        )

    @Test
    fun replacesAndRemovesLocationsUsingFullKeys() {
        val index = PositionalDeleteIndex(keySchema.asStruct())
        val firstKey =
            keySchema.asStruct().let { schema ->
                org.apache.iceberg.data.GenericRecord.create(schema).apply {
                    setField("id", 7)
                    setField("tenant", "one")
                }
            }
        val equivalentKey =
            keySchema.asStruct().let { schema ->
                org.apache.iceberg.data.GenericRecord.create(schema).apply {
                    setField("id", 7)
                    setField("tenant", "one")
                }
            }
        val location =
            PositionalDeleteIndex.RowLocation(
                "s3://bucket/data.parquet",
                3L,
                org.apache.iceberg.PartitionSpec.unpartitioned(),
                null,
            )

        assertNull(index.replace(firstKey, location))
        assertEquals(location, index.get(equivalentKey))
        assertEquals(location, index.remove(equivalentKey))
        assertEquals(0, index.size())
        assertEquals(1L, index.maxEntries())
    }
}
