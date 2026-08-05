/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.nio.ByteBuffer
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Comparators
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class TouchedKeysTest {
    @Test
    fun `budget flush retains earlier same-flush location for a later repeat`() {
        val schema =
            Schema(
                listOf(Types.NestedField.required(1, "id", Types.StringType.get())),
                setOf(1),
            )
        val keys = TouchedKeys(schema.asStruct(), maximum = 1)
        val spec = PartitionSpec.unpartitioned()
        val first = PositionalDeleteResolver.RowLocation("file-a", 0, spec, null)
        val second = PositionalDeleteResolver.RowLocation("file-a", 1, spec, null)
        val key = GenericRecord.create(schema).apply { setField("id", "one") }

        keys.markWritten(key, first)
        assertThat(keys.isFull()).isTrue()
        keys.clear()
        keys.markWritten(key, second)

        assertThat(keys.supersededWithinFlush().toList()).containsExactly(first)
    }

    @Test
    fun `budget flush includes repeated same-flush superseded locations`() {
        val schema =
            Schema(
                listOf(Types.NestedField.required(1, "id", Types.StringType.get())),
                setOf(1),
            )
        val keys = TouchedKeys(schema.asStruct(), maximum = 3)
        val spec = PartitionSpec.unpartitioned()
        val key = GenericRecord.create(schema).apply { setField("id", "one") }

        keys.markWritten(key, PositionalDeleteResolver.RowLocation("file-a", 0, spec, null))
        keys.markWritten(key, PositionalDeleteResolver.RowLocation("file-a", 1, spec, null))
        assertThat(keys.isFull()).isFalse()
        keys.markWritten(key, PositionalDeleteResolver.RowLocation("file-a", 2, spec, null))

        assertThat(keys.isFull()).isTrue()
        assertThat(keys.supersededWithinFlush().toList()).hasSize(2)
    }

    @Test
    fun `distinct current writes have a defensive aggregate ceiling`() {
        val schema =
            Schema(
                listOf(Types.NestedField.required(1, "id", Types.StringType.get())),
                setOf(1),
            )
        val keys =
            TouchedKeys(
                schema.asStruct(),
                maximum = 10,
                maximumCurrentWrites = 2,
            )
        val spec = PartitionSpec.unpartitioned()

        keys.markInserted(
            GenericRecord.create(schema).apply { setField("id", "one") },
            PositionalDeleteResolver.RowLocation("file-a", 0, spec, null),
        )
        keys.markInserted(
            GenericRecord.create(schema).apply { setField("id", "two") },
            PositionalDeleteResolver.RowLocation("file-a", 1, spec, null),
        )

        assertThatThrownBy {
                keys.markInserted(
                    GenericRecord.create(schema).apply { setField("id", "three") },
                    PositionalDeleteResolver.RowLocation("file-a", 2, spec, null),
                )
            }
            .isInstanceOf(IllegalStateException::class.java)
            .hasMessageContaining("aggregate record configuration")
    }

    @Test
    fun `membership supports multi-column identifiers`() {
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "tenant", Types.StringType.get()),
                    Types.NestedField.required(2, "id", Types.IntegerType.get()),
                ),
                setOf(1, 2),
            )
        val keys = TouchedKeys(schema.asStruct())
        val key =
            GenericRecord.create(schema).apply {
                setField("tenant", "acme")
                setField("id", 7)
            }
        val location =
            PositionalDeleteResolver.RowLocation(
                "file-a",
                3,
                PartitionSpec.unpartitioned(),
                null,
            )

        keys.markWritten(key, location)

        val storedKey = keys.keys().single()
        assertThat(storedKey.get(0, String::class.java)).isEqualTo("acme")
        assertThat(storedKey.get(1, Int::class.javaObjectType)).isEqualTo(7)
    }

    @Test
    fun `iceberg comparator supports binary identifier values`() {
        val comparator = Comparators.forType<Any>(Types.BinaryType.get())
        val lower = ByteBuffer.wrap(byteArrayOf(1))
        val upper = ByteBuffer.wrap(byteArrayOf(2))

        assertThat(comparator.compare(lower, upper)).isNegative()
    }
}
