/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.fusion.FusionConfiguration
import io.airbyte.cdk.fusion.FusionUploader

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.json.AirbyteTypeToJsonSchema
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.mockk.every
import io.mockk.mockk
import java.nio.file.Path
import java.util.UUID
import java.util.concurrent.CompletableFuture
import kotlinx.coroutines.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class SnowflakeStreamCompletionTest {
    @Test
    fun `refresh setup writes only schema and empty completion contains job and cutoff`() =
        runBlocking {
            val fixture = Fixture(42)
            fixture.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(fixture.stream)))
                assertEquals(
                    listOf("schema.json"),
                    fixture.uploader.keys.map { it.substringAfterLast('/') }
                )
                copy.complete(fixture.stream)
                copy.complete(fixture.stream)
                val key = copy.context(fixture.stream)!!.runPath + "batches/stream_complete.json"
                assertEquals(
                    listOf("schema.json", "stream_complete.json"),
                    fixture.uploader.keys.map { it.substringAfterLast('/') }
                )
                assertEquals(
                    "{\"job_id\":12345,\"min_generation_id\":42}",
                    fixture.uploader.json.getValue(key)
                )
            }
        }

    @Test
    fun `completion waits for durable marker and failed put may retry same key`() = runBlocking {
        val fixture = Fixture(0)
        fixture.copy.use { copy ->
            copy.prepare(DestinationCatalog(listOf(fixture.stream)))
            fixture.uploader.markerResult =
                CompletableFuture.failedFuture<Unit>(IllegalStateException("S3 failed"))
            assertThrows(Exception::class.java) { runBlocking { copy.complete(fixture.stream) } }
            val pending = CompletableFuture<Unit>()
            fixture.uploader.markerResult = pending
            val completion = async { copy.complete(fixture.stream) }
            delay(100)
            assertFalse(completion.isCompleted)
            pending.complete(Unit)
            completion.await()
            val key = copy.context(fixture.stream)!!.runPath + "batches/stream_complete.json"
            assertEquals("{\"job_id\":12345}", fixture.uploader.json.getValue(key))
            assertEquals(2, fixture.uploader.keys.count { it == key })
        }
    }

    @Test
    fun `schema retains original configured primary key and cursor for append streams`() =
        runBlocking {
            val configured =
                ConfiguredAirbyteStream()
                    .withStream(AirbyteStream().withName("Orders/日本").withNamespace("public"))
                    .withPrimaryKey(listOf(listOf("id"), listOf("nested", "key")))
                    .withCursorField(listOf("updated_at"))
            val fixture = Fixture(0, ConfiguredAirbyteCatalog().withStreams(listOf(configured)))
            fixture.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(fixture.stream)))
                val schema = Jsons.readTree(fixture.uploader.json.values.single())
                assertEquals(
                    listOf(listOf("id"), listOf("nested", "key")),
                    schema["primary_key"].map { it.map { field -> field.asText() } }
                )
                assertEquals(listOf("updated_at"), schema["cursor"].map { it.asText() })
            }
            val unconfigured = Fixture(0)
            unconfigured.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(unconfigured.stream)))
                val schema = Jsons.readTree(unconfigured.uploader.json.values.single())
                assertTrue(schema["primary_key"].isArray && schema["primary_key"].isEmpty)
                assertTrue(schema["cursor"].isArray && schema["cursor"].isEmpty)
            }
        }

    @ParameterizedTest
    @CsvSource("false,false", "false,true", "true,false", "true,true")
    fun `schema includes source fields in raw and typed modes`(raw: Boolean, withCatalog: Boolean) =
        runBlocking {
            val originalSchema =
                Jsons.readTree(
                    """{
                  "type":"object", "required":["id"], "additionalProperties":false,
                  "properties":{
                    "id":{"type":"integer", "description":"Source identifier", "minimum":0},
                    "nested":{"type":"object", "properties":{"key":{"type":"string", "enum":["a","b"]}}}
                  }
                }"""
                )
            val configured =
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withName("Orders/日本")
                            .withNamespace("public")
                            .withJsonSchema(originalSchema)
                    )
            // A same-name stream in another namespace must not be selected.
            val other =
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withName("Orders/日本")
                            .withNamespace("other")
                            .withJsonSchema(Jsons.readTree("{}"))
                    )
            val catalog =
                if (withCatalog) ConfiguredAirbyteCatalog().withStreams(listOf(other, configured))
                else null
            val fixture = Fixture(0, catalog, raw)
            fixture.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(fixture.stream)))
                val schema = Jsons.readTree(fixture.uploader.json.values.single())
                val expected =
                    if (withCatalog) originalSchema
                    else
                        AirbyteTypeToJsonSchema()
                            .convert(
                                ObjectType(
                                    LinkedHashMap(
                                        fixture.stream.tableSchema.columnSchema.inputSchema
                                    )
                                )
                            )
                assertEquals(expected, schema["source_schema"])
                assertTrue(schema["source_schema"]["properties"].has("id"))
                assertTrue(schema["source_schema"]["properties"]["nested"]["properties"].has("key"))
                assertEquals(raw, schema["columns"].has("_airbyte_data"))
                assertEquals(!raw, schema["columns"].has("ID"))
                assertEquals(if (raw) "raw" else "schema", schema["mode"].asText())
                if (withCatalog) {
                    configured.stream.jsonSchema =
                        Jsons.readTree(
                            originalSchema
                                .toString()
                                .replace("Source identifier", "Updated description")
                        )
                    val changed = Fixture(0, catalog, raw)
                    changed.copy.use { next ->
                        next.prepare(DestinationCatalog(listOf(changed.stream)))
                        val nextSchema = Jsons.readTree(changed.uploader.json.values.single())
                        assertNotEquals(schema["schema_id"], nextSchema["schema_id"])
                    }
                }
            }
        }

    private class Fixture(
        minimum: Long,
        configuredCatalog: ConfiguredAirbyteCatalog? = null,
        raw: Boolean = false
    ) {
        private val configuration =
            mockk<SnowflakeConfiguration>(relaxed = true) {
                every { legacyRawTablesOnly } returns raw
            }
        val stream =
            mockk<DestinationStream> {
                every { unmappedName } returns "Orders/日本"
                every { unmappedNamespace } returns "public"
                every { mappedDescriptor } returns DestinationStream.Descriptor("public", "orders")
                every { syncId } returns 12345L
                every { generationId } returns 42L
                every { minimumGenerationId } returns minimum
                every { tableSchema } returns
                    StreamTableSchema(
                        TableNames(finalTableName = TableName("public", "orders")),
                        ColumnSchema(
                            linkedMapOf(
                                "id" to FieldType(IntegerType, false),
                                "nested" to
                                    FieldType(
                                        ObjectType(
                                            linkedMapOf("key" to FieldType(StringType, true))
                                        ),
                                        true
                                    )
                            ),
                            mapOf("id" to "ID", "nested" to "NESTED"),
                            if (raw) mapOf("_airbyte_data" to ColumnType("VARIANT", false))
                            else
                                mapOf(
                                    "ID" to ColumnType("NUMBER", false),
                                    "NESTED" to ColumnType("VARIANT", true)
                                )
                        ),
                        Append,
                    )
            }
        val uploader = FakeUploader()
        val copy =
            EnabledSnowflakeS3Copy(
                FusionConfiguration(
                    "role",
                    "bucket",
                    "us-west-2",
                    UUID(0, 4),
                    UUID(0, 2),
                    UUID(0, 3),
                    "fusion",
                    null,
                    UUID(0, 1),
                    UUID(0, 5),
                ),
                SnowflakeColumnManager(configuration),
                configuration,
                uploader,
                configuredCatalog,
            )
    }
    private class FakeUploader : FusionUploader {
        val keys = mutableListOf<String>()
        val json = mutableMapOf<String, String>()
        var markerResult: CompletableFuture<*> = CompletableFuture.completedFuture(Unit)
        override fun upload(
            path: Path,
            key: String,
            metadata: Map<String, String>
        ): CompletableFuture<*> = error("No data in empty stream")
        override fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<*> {
            keys.add(key)
            json[key] = Jsons.writeValueAsString(Jsons.readTree(String(bytes, Charsets.UTF_8)))
            return if (key.endsWith("stream_complete.json")) markerResult
            else CompletableFuture.completedFuture(Unit)
        }
        override fun close() = Unit
    }
}
