/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.cdk.discover.OffsetDateTimeFieldType
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.discover.TestMetaFieldDecorator
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DebeziumPropertiesBuilderTest {

    @Test
    fun testWithDatabase() {
        val actual: Map<String, String> =
            DebeziumPropertiesBuilder()
                .withDatabase(
                    mapOf(
                        "host" to "localhost",
                        "port" to "12345",
                    )
                )
                .buildMap()
        Assertions.assertEquals(
            mapOf(
                "database.host" to "localhost",
                "database.port" to "12345",
            ),
            actual
        )
    }

    @Test
    fun testWithStreams() {
        fun stream(namespace: String, name: String, vararg fields: Field): Stream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withName(name).withNamespace(namespace)
                    ),
                schema = fields.toSet() + setOf(TestMetaFieldDecorator.GlobalCursor),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = null,
                configuredCursor = TestMetaFieldDecorator.GlobalCursor,
            )
        val streams: List<Stream> =
            listOf(
                stream("schema1", "table1", Field("k", IntFieldType), Field("v", StringFieldType)),
                stream(
                    "schema2",
                    "table2",
                    Field("id", IntFieldType),
                    Field("ts", OffsetDateTimeFieldType),
                    Field("msg", StringFieldType)
                ),
            )
        val actual: Map<String, String> =
            DebeziumPropertiesBuilder().withStreams(streams).buildMap()
        Assertions.assertEquals(
            mapOf(
                "table.include.list" to """\Qschema1.table1\E,\Qschema2.table2\E""",
                "column.include.list" to
                    """\Qschema1.table1\E\.(\Qk\E|\Qv\E),\Qschema2.table2\E\.(\Qid\E|\Qts\E|\Qmsg\E)"""
            ),
            actual
        )
    }

    @Test
    fun testWithDebeziumName() {
        val actual: Map<String, String> =
            DebeziumPropertiesBuilder().withDebeziumName("_.-#L33T!-._").buildMap()
        Assertions.assertEquals(
            mapOf(
                "name" to "_.-#L33T!-._",
                "topic.prefix" to "_.-_L33T_-._",
            ),
            actual
        )
    }

    @Test
    fun testWithOffset() {
        val validPath = Path.of(".")
        val b = DebeziumPropertiesBuilder()
        Assertions.assertFalse(b.expectsOffsetFile)
        Assertions.assertEquals(0, b.withOffsetFile(validPath).buildMap().size)
        b.withOffset()
        Assertions.assertEquals(
            mapOf(
                "offset.storage" to "org.apache.kafka.connect.storage.FileOffsetBackingStore",
            ),
            b.buildMap()
        )
        Assertions.assertTrue(b.expectsOffsetFile)
        b.withOffsetFile(validPath)

        Assertions.assertEquals(
            mapOf(
                "offset.storage" to "org.apache.kafka.connect.storage.FileOffsetBackingStore",
                "offset.storage.file.filename" to ".",
            ),
            b.buildMap()
        )
    }

    @Test
    fun testWithSchemaHistory() {
        val validPath = Path.of(".")
        val b = DebeziumPropertiesBuilder()
        Assertions.assertFalse(b.expectsSchemaHistoryFile)
        Assertions.assertEquals(0, b.withSchemaHistoryFile(validPath).buildMap().size)
        b.withSchemaHistory()
        Assertions.assertEquals(
            mapOf(
                "schema.history.internal" to "io.debezium.storage.file.history.FileSchemaHistory",
                "schema.history.internal.store.only.captured.databases.ddl" to "true"
            ),
            b.buildMap()
        )
        Assertions.assertTrue(b.expectsSchemaHistoryFile)
        b.withSchemaHistoryFile(validPath)
        Assertions.assertEquals(
            mapOf(
                "schema.history.internal" to "io.debezium.storage.file.history.FileSchemaHistory",
                "schema.history.internal.store.only.captured.databases.ddl" to "true",
                "schema.history.internal.file.filename" to ".",
            ),
            b.buildMap()
        )
    }
}
