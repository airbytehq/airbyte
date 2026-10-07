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
import io.airbyte.protocol.models.v0.DestinationSyncMode
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
import org.junit.jupiter.params.provider.ValueSource

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
            assertEquals(
                "{\"job_id\":12345,\"min_generation_id\":0}",
                fixture.uploader.json.getValue(key)
            )
            assertEquals(2, fixture.uploader.keys.count { it == key })
        }
    }

    @Test
    fun `schema retains original configured primary key and cursor for append streams`() =
        runBlocking {
            val configured =
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withName("Orders/日本")
                            .withNamespace("public")
                            .withJsonSchema(Jsons.readTree("{}"))
                    )
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
    @ValueSource(booleans = [false, true])
    fun `prepare preserves deselected configured keys and cursor for append streams`(raw: Boolean) =
        runBlocking {
            val sourceSchema =
                Jsons.readTree("""{"type":"object","properties":{"name":{"type":"string"}}}""")
            val configured =
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withName("Orders/日本")
                            .withNamespace("public")
                            .withJsonSchema(sourceSchema)
                    )
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withPrimaryKey(listOf(listOf("id")))
                    .withCursorField(listOf("updated_at"))
            val fixture =
                Fixture(0, ConfiguredAirbyteCatalog().withStreams(listOf(configured)), raw)
            // Only name is selected; configured metadata need not have an output mapping.
            every { fixture.stream.tableSchema } returns
                StreamTableSchema(
                    TableNames(finalTableName = TableName("public", "orders")),
                    ColumnSchema(
                        linkedMapOf("name" to FieldType(StringType, true)),
                        mapOf("name" to "NAME"),
                        if (raw) mapOf("_airbyte_data" to ColumnType("VARIANT", false))
                        else mapOf("NAME" to ColumnType("TEXT", true)),
                    ),
                    Append,
                )
            fixture.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(fixture.stream)))
                val context = checkNotNull(copy.context(fixture.stream))
                assertEquals(listOf(context.runPath + "schema.json"), fixture.uploader.keys)
                val schema = Jsons.readTree(fixture.uploader.json.values.single())
                assertEquals(sourceSchema, schema["source_schema"])
                assertEquals(Jsons.readTree("""[["id"]]"""), schema["primary_key"])
                assertEquals(Jsons.readTree("""["updated_at"]"""), schema["cursor"])
                assertEquals(Jsons.readTree("""{"name":"NAME"}"""), schema["input_to_final"])
                assertEquals(if (raw) "raw" else "schema", schema["mode"].asText())
                assertEquals(raw, schema["columns"].has("_airbyte_data"))
                assertEquals(!raw, schema["columns"].has("NAME"))
                assertFalse(schema["columns"].has("ID"))
                assertFalse(schema["columns"].has("UPDATED_AT"))
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

    @Test
    fun `same named streams in different namespaces have separate schemas batches and completion`() =
        runBlocking {
            val publicSchema =
                Jsons.readTree(
                    """{"type":"object","properties":{"public_id":{"type":"integer"}}}"""
                )
            val billingSchema =
                Jsons.readTree(
                    """{"type":"object","properties":{"billing_id":{"type":"string"}}}"""
                )
            fun configured(namespace: String, schema: com.fasterxml.jackson.databind.JsonNode) =
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withName("Orders/日本")
                            .withNamespace(namespace)
                            .withJsonSchema(schema)
                    )
            val fixture =
                Fixture(
                    0,
                    ConfiguredAirbyteCatalog()
                        .withStreams(
                            listOf(
                                configured("public", publicSchema),
                                configured("billing", billingSchema)
                            )
                        )
                )
            val billingFixture = Fixture(0)
            val billing = billingFixture.stream
            billingFixture.copy.close()
            every { billing.unmappedNamespace } returns "billing"
            every { billing.mappedDescriptor } returns
                DestinationStream.Descriptor("billing", "orders")
            fixture.copy.use { copy ->
                copy.prepare(DestinationCatalog(listOf(fixture.stream, billing)))
                val publicContext = copy.context(fixture.stream)!!
                val billingContext = copy.context(billing)!!
                assertEquals(
                    publicContext.runPath.substringAfter("/runs/"),
                    billingContext.runPath.substringAfter("/runs/")
                )
                assertNotEquals(publicContext.runPath, billingContext.runPath)
                assertTrue(
                    publicContext.runPath.contains(
                        "/streams/public/Orders%2F%E6%97%A5%E6%9C%AC/runs/"
                    )
                )
                assertTrue(
                    billingContext.runPath.contains(
                        "/streams/billing/Orders%2F%E6%97%A5%E6%9C%AC/runs/"
                    )
                )
                assertEquals(2, fixture.uploader.json.size)
                assertEquals(
                    publicSchema,
                    Jsons.readTree(
                            fixture.uploader.json.getValue(publicContext.runPath + "schema.json")
                        )["source_schema"]
                )
                assertEquals(
                    billingSchema,
                    Jsons.readTree(
                            fixture.uploader.json.getValue(billingContext.runPath + "schema.json")
                        )["source_schema"]
                )
                val path = java.nio.file.Files.createTempFile("namespace-copy", ".csv.gz")
                try {
                    copy.upload(path, publicContext, 1)
                    copy.upload(path, billingContext, 1)
                } finally {
                    java.nio.file.Files.deleteIfExists(path)
                }
                copy.complete(fixture.stream)
                copy.complete(billing)
                assertEquals(6, fixture.uploader.keys.size)
                assertEquals(6, fixture.uploader.keys.toSet().size)
                listOf(publicContext, billingContext).forEach { context ->
                    val batch =
                        fixture.uploader.keys.single {
                            it.startsWith(context.runPath + "batches/") && it.endsWith(".csv.gz")
                        }
                    val batchId =
                        batch.removePrefix(context.runPath + "batches/").removeSuffix(".csv.gz")
                    assertEquals(batchId, UUID.fromString(batchId).toString())
                    assertEquals(batchId, fixture.uploader.metadata.getValue(batch)["batch-id"])
                    assertTrue(
                        fixture.uploader.keys.contains(
                            context.runPath + "batches/stream_complete.json"
                        )
                    )
                }
            }
        }

    @Test
    fun `oversized namespace fails preflight before any schemas are uploaded`() = runBlocking {
        val fixture = Fixture(0)
        val invalidFixture = Fixture(0)
        invalidFixture.copy.close()
        every { invalidFixture.stream.unmappedNamespace } returns "界".repeat(120)
        every { invalidFixture.stream.mappedDescriptor } returns
            DestinationStream.Descriptor("invalid", "orders")
        fixture.copy.use { copy ->
            assertThrows(IllegalArgumentException::class.java) {
                runBlocking {
                    copy.prepare(DestinationCatalog(listOf(fixture.stream, invalidFixture.stream)))
                }
            }
            assertTrue(fixture.uploader.keys.isEmpty())
            assertNull(copy.context(fixture.stream))
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
                    roleArn = "role",
                    externalId = null,
                    bucket = "bucket",
                    region = "us-west-2",
                    connectionId = UUID(0, 4),
                    workspaceId = UUID(0, 2),
                    sourceId = UUID(0, 3),
                    prefix = "fusion",
                    organizationId = UUID(0, 1),
                    destinationId = UUID(0, 5),
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
        val metadata = mutableMapOf<String, Map<String, String>>()
        var markerResult: CompletableFuture<*> = CompletableFuture.completedFuture(Unit)
        override fun upload(
            path: Path,
            key: String,
            metadata: Map<String, String>
        ): CompletableFuture<*> {
            keys.add(key)
            this.metadata[key] = metadata
            return CompletableFuture.completedFuture(Unit)
        }
        override fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<*> {
            keys.add(key)
            json[key] = Jsons.writeValueAsString(Jsons.readTree(String(bytes, Charsets.UTF_8)))
            return if (key.endsWith("stream_complete.json")) markerResult
            else CompletableFuture.completedFuture(Unit)
        }
        override fun close() = Unit
    }
}
