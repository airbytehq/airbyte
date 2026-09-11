/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryObjectStorageFormattingWriterFactory
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.StringReader
import java.nio.file.Files
import java.nio.file.Path
import java.time.OffsetDateTime
import java.util.UUID
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import kotlinx.coroutines.runBlocking
import org.apache.commons.csv.CSVFormat
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class BigqueryCopyMetadataTest {
    @TempDir lateinit var directory: Path
    private val runId = UUID.fromString("11111111-1111-1111-1111-111111111111")
    private val config =
        S3CopyConfiguration(
            roleArn = "arn:aws:iam::123456789012:role/archive",
            bucket = "archive",
            region = "us-east-1",
            connectionId = UUID.fromString("22222222-2222-2222-2222-222222222222"),
            workspaceId = UUID.fromString("33333333-3333-3333-3333-333333333333"),
            sourceId = UUID.fromString("44444444-4444-4444-4444-444444444444"),
            prefix = "fusion",
            externalId = null,
        )
    private val schema =
        ObjectType(
            linkedMapOf(
                "z field" to FieldType(StringType, true),
                "id" to FieldType(IntegerType, false),
                "empty" to FieldType(StringType, true),
                "literal" to FieldType(StringType, true),
                "missing" to FieldType(StringType, true),
                "nil" to FieldType(StringType, true),
                "nested" to
                    FieldType(ObjectType(linkedMapOf("key" to FieldType(StringType, true))), true),
                "ts" to FieldType(TimestampTypeWithTimezone, true),
            )
        )
    private val payload =
        Jsons.readTree(
            """{"z field":"É雪,\"quoted\"\nnext","id":7,"empty":"","literal":"\\N","nil":null,"nested":{"key":"value"},"ts":"2026-09-10T01:02:03+02:00","undeclared":"preserved in raw JSON"}"""
        )

    @ParameterizedTest
    @CsvSource("false,JSONL", "false,PROTOBUF", "true,JSONL", "true,PROTOBUF")
    fun `descriptor matches real compressed formatter headers and values`(
        raw: Boolean,
        format: DataChannelFormat,
    ) {
        val stream = stream()
        val metadata = metadata(stream, raw, format)
        val descriptor = tree(metadata.descriptor(stream))
        val layout = descriptor["layout"]
        val bytes = bigqueryCopyFormattedGzip(stream, bigquery(raw), format, record(stream, format))
        // Exercise the complete copy path with the same bytes described below, including metadata
        // preparation, GCS callback, closed-file spool, uploader and cleanup, for all four formats.
        runBlocking {
            val blob = GcsBlob("completed.csv.gz", mockk())
            val storage = mockk<GcsClient>()
            coEvery { storage.get<Long>(blob.key, any()) } coAnswers
                {
                    secondArg<(InputStream) -> Long>().invoke(ByteArrayInputStream(bytes))
                }
            val uploadedKeys = mutableListOf<String>()
            val uploadedData = mutableListOf<ByteArray>()
            val uploader =
                object : ArchiveUploader {
                    override suspend fun validateCredentials() = Unit

                    override fun close() = Unit

                    override suspend fun upload(
                        path: Path,
                        key: String,
                        contentType: String,
                        metadata: Map<String, String>,
                    ) {
                        uploadedKeys.add(key)
                        when (contentType) {
                            "application/json" ->
                                assertEquals(descriptor, Jsons.readTree(Files.readString(path)))
                            "application/gzip" -> {
                                uploadedData.add(Files.readAllBytes(path))
                                assertEquals(
                                    descriptor["schema_id"].asText(),
                                    metadata["schema-id"],
                                )
                                assertEquals("1", metadata["loaded-record-count"])
                                assertTrue(
                                    key.startsWith(
                                        "${this@BigqueryCopyMetadataTest.metadata(stream, raw, format).runPath(stream)}/batches/"
                                    )
                                )
                            }
                            else -> fail<Unit>("Unexpected upload content type: $contentType")
                        }
                    }
                }
            EnabledBigqueryS3Copy(
                    config,
                    bigquery(raw),
                    metadata,
                    runId,
                    { uploader },
                    spoolDirectory = directory,
                )
                .use { archive ->
                    archive.prepare(DestinationCatalog(listOf(stream)))
                    archive.copyCompletedGcsObject(storage, blob, archive.context(stream), 1)
                }
            assertEquals(2, uploadedKeys.size)
            assertTrue(uploadedKeys[0].endsWith("/schema.json"))
            assertTrue(uploadedKeys[1].endsWith(".csv.gz"))
            assertArrayEquals(bytes, uploadedData.single())
            assertEquals(0L, Files.list(directory).use { it.count() })
            coVerify(exactly = 1) { storage.get<Long>(blob.key, any()) }
            coVerify(exactly = 0) { storage.delete(any<GcsBlob>()) }
        }
        val csv =
            GZIPInputStream(bytes.inputStream()).bufferedReader(Charsets.UTF_8).use {
                it.readText()
            }
        val records = CSVFormat.DEFAULT.parse(StringReader(csv)).use { it.records }
        val headers = records[0].toList()
        val row = records[1]
        assertEquals(2, records.size)
        assertEquals(layout["columns"].map { it["csv_header"].asText() }, headers)
        assertEquals(headers.indices.toList(), layout["columns"].map { it["csv_ordinal"].asInt() })
        assertEquals(format.name, layout["input_format"].asText())
        assertEquals("\r\n", layout["csv"]["record_separator"].asText())
        assertTrue(csv.endsWith("\r\n"))
        assertTrue(csv.startsWith("\"_airbyte_raw_id\",\"_airbyte_extracted_at\""))
        assertEquals(runId.toString(), row[0])
        assertEquals(42L, Jsons.readTree(row[2])["sync_id"].asLong())
        assertEquals("9", row[3])
        if (raw) {
            assertEquals(
                listOf(
                    "_airbyte_raw_id",
                    "_airbyte_extracted_at",
                    "_airbyte_meta",
                    "_airbyte_generation_id",
                    "_airbyte_data",
                ),
                headers,
            )
            assertFalse(headers.contains("_airbyte_loaded_at"))
            assertTrue(
                BigQueryRecordFormatter.SCHEMA_V2.fields.any { it.name == "_airbyte_loaded_at" }
            )
            val data = Jsons.readTree(row[4])
            assertEquals(payload["z field"], data["z field"])
            assertEquals(payload["nested"], data["nested"])
            assertEquals("", data["empty"].asText())
            assertEquals("\\N", data["literal"].asText())
            assertTrue(data["nil"].isNull)
            assertEquals(format == DataChannelFormat.JSONL, data.has("undeclared"))
            assertEquals(format == DataChannelFormat.PROTOBUF, data.has("missing"))
            assertEquals("STRING", layout["columns"][4]["type"].asText())
            assertTrue(csv.contains(",9,"))
        } else {
            assertEquals("z field", headers[4])
            assertEquals("mapped_0", layout["columns"][4]["target_field"].asText())
            assertEquals(payload["z field"].asText(), row[4])
            assertEquals("7", row[headers.indexOf("id")])
            assertEquals("", row[headers.indexOf("empty")])
            listOf("literal", "nil", "missing").forEach {
                assertEquals("\\N", row[headers.indexOf(it)])
            }
            assertEquals(payload["nested"], Jsons.readTree(row[headers.indexOf("nested")]))
            assertEquals("2026-09-10T01:02:03+02:00", row[headers.indexOf("ts")])
            assertEquals("REQUIRED", layout["columns"][0]["mode"].asText())
            // BigQuery load fields are nullable even when the catalog declares a nonnullable id.
            assertTrue(layout["columns"][5]["nullable"].asBoolean())
            assertEquals(
                "JSON",
                layout["columns"].first { it["csv_header"].asText() == "nested" }["type"].asText(),
            )
            assertTrue(csv.contains(",\"\\N\","))
            assertTrue(csv.contains(if (format == DataChannelFormat.PROTOBUF) ",\"9\"," else ",9,"))
        }
        assertEquals(
            if (!raw && format == DataChannelFormat.PROTOBUF) "1970-01-01 00:00:01.234000+00:00"
            else "1970-01-01T00:00:01.234Z",
            row[1],
        )
        assertEquals(
            metadata.schemaId(metadata.descriptor(stream)),
            descriptor["schema_id"].asText(),
        )
        assertEquals("CSV", layout["load_options"]["format"].asText())
        assertEquals(1, layout["load_options"]["skipLeadingRows"].asInt())
        assertEquals("\\N", layout["load_options"]["nullMarker"].asText())
        assertTrue(layout["load_options"]["allowQuotedNewLines"].asBoolean())
        assertTrue(layout["load_options"]["allowJaggedRows"].asBoolean())
        assertTrue(layout["load_options"]["preserveAsciiControlCharacters"].asBoolean())
        assertEquals("WRITE_APPEND", layout["load_options"]["writeDisposition"].asText())
    }

    @Test
    fun `configured keys and cursor retain paths and map to actual CSV columns`() {
        val stream =
            stream()
                .copy(
                    importType = Dedupe(listOf(listOf("id"), listOf("nested", "key")), listOf("ts"))
                )
        for (raw in listOf(false, true)) {
            val descriptor = tree(metadata(stream, raw).descriptor(stream))
            val layout = descriptor["layout"]
            assertEquals("APPEND_DEDUP", layout["import_type"].asText())
            assertEquals(
                listOf(listOf("id"), listOf("nested", "key")),
                layout["primary_key"].map { it.map(JsonNode::asText) },
            )
            assertEquals(listOf("ts"), layout["cursor"].map(JsonNode::asText))
            val nested = layout["primary_key_mapping"][1]
            val cursor = layout["cursor_mapping"][0]
            assertEquals(if (raw) "_airbyte_data" else "mapped_6", nested["target_column"].asText())
            assertEquals(
                if (raw) listOf("nested", "key") else listOf("key"),
                nested["path_within_column"].map(JsonNode::asText),
            )
            assertEquals(if (raw) 4 else 11, cursor["csv_ordinal"].asInt())
            assertEquals(if (raw) "_airbyte_data" else "mapped_7", cursor["target_column"].asText())
            assertEquals(
                if (raw) "_airbyte_data" else "mapped_7",
                layout["deduplication_cursor"]["target_column"].asText(),
            )
            assertEquals(
                if (raw) listOf("ts") else emptyList<String>(),
                layout["deduplication_cursor"]["path_within_column"].map(JsonNode::asText),
            )
            assertFalse(layout["deduplication_cursor"]["performed_in_raw_mode"].asBoolean())
            assertEquals(
                if (raw) "raw_dataset" else "mapped_dataset",
                descriptor["logical_table"]["dataset"].asText(),
            )
            assertEquals(
                if (raw) "raw_table" else "mapped_table",
                descriptor["logical_table"]["table"].asText(),
            )
        }
        val fallback = stream.copy(importType = Dedupe(listOf(listOf("id")), emptyList()))
        val layout = tree(metadata(fallback).descriptor(fallback))["layout"]
        assertTrue(layout["cursor"].isEmpty)
        assertTrue(layout["cursor_mapping"].isEmpty)
        assertFalse(layout["deduplication_cursor"]["configured"].asBoolean())
        assertEquals(
            "_airbyte_extracted_at",
            layout["deduplication_cursor"]["target_column"].asText(),
        )
        val append = tree(metadata(stream()).descriptor(stream()))["layout"]
        assertTrue(append["primary_key"].isEmpty)
        assertTrue(append["cursor"].isEmpty)
        assertTrue(append["deduplication_cursor"].isNull)
    }

    @Test
    fun `append retains configured keys and cursor from original catalog`() {
        val stream = stream().copy(namespaceMapper = NamespaceMapper(streamPrefix = "destination_"))
        val configured =
            stream
                .asProtocolObject()
                .withPrimaryKey(listOf(listOf("id"), listOf("nested", "key")))
                .withCursorField(listOf("ts"))
        val catalog = ConfiguredAirbyteCatalog().withStreams(listOf(configured))
        for (raw in listOf(false, true)) {
            val metadata =
                BigqueryCopyMetadata(
                    config,
                    bigquery(raw),
                    names(stream),
                    runId,
                    DataChannelFormat.JSONL,
                    catalog,
                )
            val layout = tree(metadata.descriptor(stream))["layout"]
            assertEquals("APPEND", layout["import_type"].asText())
            assertEquals(
                listOf(listOf("id"), listOf("nested", "key")),
                layout["primary_key"].map { it.map(JsonNode::asText) },
            )
            assertEquals(listOf("ts"), layout["cursor"].map(JsonNode::asText))
            assertEquals(
                if (raw) "_airbyte_data" else "mapped_1",
                layout["primary_key_mapping"][0]["target_column"].asText(),
            )
            assertEquals(
                if (raw) "_airbyte_data" else "mapped_7",
                layout["cursor_mapping"][0]["target_column"].asText(),
            )
            assertTrue(layout["deduplication_cursor"].isNull)
        }
    }

    @Test
    fun `canonical hash ignores attempts and map insertion order but preserves array order`() {
        val stream = stream()
        val metadata = metadata(stream)
        val descriptor = metadata.descriptor(stream)
        val serialized = Jsons.readTree(metadata.serialize(descriptor))
        assertEquals(
            descriptor["schema_id"],
            metadata.schemaId(mapOf("layout" to serialized["layout"])),
        )
        val retry = stream.copy(syncId = 888, generationId = 100, minimumGenerationId = 100)
        val retryMetadata = metadata(retry, run = UUID.randomUUID())
        assertEquals(descriptor["schema_id"], retryMetadata.descriptor(retry)["schema_id"])
        assertNotEquals(metadata.runPath(stream), retryMetadata.runPath(retry))
        assertEquals(metadata.streamKey(stream), retryMetadata.streamKey(retry))
        assertEquals(
            metadata.schemaId(descriptor),
            metadata.schemaId(
                descriptor +
                    mapOf(
                        "run_id" to "another",
                        "connector_version" to "next",
                        "schema_id" to "ignored",
                    )
            ),
        )
        val layoutA =
            linkedMapOf(
                "columns" to
                    listOf(
                        mapOf("type" to "STRING", "name" to "a"),
                        mapOf("name" to "b", "type" to "INT64"),
                    ),
                "csv" to mapOf("quote" to "\"", "separator" to ","),
            )
        val layoutB =
            linkedMapOf(
                "csv" to linkedMapOf("separator" to ",", "quote" to "\""),
                "columns" to
                    listOf(
                        linkedMapOf("name" to "a", "type" to "STRING"),
                        linkedMapOf("type" to "INT64", "name" to "b"),
                    ),
            )
        assertEquals(
            metadata.schemaId(mapOf("layout" to layoutA)),
            metadata.schemaId(mapOf("layout" to layoutB)),
        )
        assertNotEquals(
            metadata.schemaId(mapOf("layout" to layoutA)),
            metadata.schemaId(
                mapOf(
                    "layout" to
                        (layoutA + ("columns" to (layoutA["columns"] as List<*>).reversed()))
                )
            ),
        )
        assertNotEquals(
            descriptor["schema_id"],
            metadata(stream, raw = true).descriptor(stream)["schema_id"],
        )
        assertNotEquals(
            descriptor["schema_id"],
            metadata(stream, format = DataChannelFormat.PROTOBUF).descriptor(stream)["schema_id"],
        )
        val changed =
            stream.copy(schema = ObjectType(linkedMapOf("id" to FieldType(StringType, true))))
        assertNotEquals(descriptor["schema_id"], metadata(changed).descriptor(changed)["schema_id"])
        val changedMapping = metadata(stream, mappingPrefix = "other_")
        assertNotEquals(descriptor["schema_id"], changedMapping.descriptor(stream)["schema_id"])
        assertTrue(metadata.schemaId(descriptor).matches(Regex("[0-9a-f]{64}")))
        assertThrows(IllegalArgumentException::class.java) { metadata.schemaId(emptyMap()) }
    }

    @Test
    fun `paths preserve original names and null namespaces without using mapped table names`() {
        val stream =
            stream()
                .copy(
                    unmappedName = "MiX/雪% .",
                    unmappedNamespace = null,
                    namespaceMapper = NamespaceMapper(streamPrefix = "mapped_"),
                )
        val metadata = metadata(stream)
        val expected =
            "fusion/workspaces/${config.workspaceId}/sources/${config.sourceId}/connections/${config.connectionId}/streams/MiX%2F%E9%9B%AA%25%20./runs/$runId"
        assertEquals(expected, metadata.runPath(stream))
        val descriptor = tree(metadata.descriptor(stream))
        assertTrue(descriptor["original_stream"]["namespace"].isNull)
        assertEquals(stream.unmappedName, descriptor["original_stream"]["name"].asText())
        assertEquals("mapped_${stream.unmappedName}", descriptor["mapped_stream"]["name"].asText())
        assertEquals(config.workspaceId.toString(), descriptor["workspace_id"].asText())
        assertEquals(config.connectionId.toString(), descriptor["connection_id"].asText())
        assertEquals(config.sourceId.toString(), descriptor["source_id"].asText())
        assertEquals("project", descriptor["logical_table"]["project"].asText())
        assertEquals(metadata.streamKey(stream), descriptor["stream_key"].asText())
        assertNotEquals(
            metadata.streamKey(stream),
            metadata.streamKey(stream.copy(unmappedName = "mix/雪% .")),
        )
        mapOf(
                "." to "%2E",
                ".." to "%2E%2E",
                "%2F" to "%252F",
                "A+ B" to "A%2B%20B",
                "é" to "%C3%A9",
            )
            .forEach { (name, escaped) ->
                assertTrue(
                    metadata
                        .runPath(stream.copy(unmappedName = name))
                        .contains("/streams/$escaped/runs/")
                )
            }
        assertThrows(IllegalArgumentException::class.java) {
            metadata.runPath(stream.copy(unmappedName = ""))
        }
    }

    @Test
    fun `cutoffs explicitly request strictly older generations with independent event ids`() {
        val stream = stream().copy(minimumGenerationId = 9)
        val metadata = metadata(stream)
        val cutoff = tree(metadata.cutoff(stream))
        assertEquals("generation_cutoff_requested", cutoff["event_type"].asText())
        assertEquals("strictly_less_than", cutoff["discard"]["comparison"].asText())
        assertEquals("_airbyte_generation_id", cutoff["discard"]["field"].asText())
        assertEquals(9, cutoff["discard"]["value"].asInt())
        assertEquals(9, cutoff["generation_id"].asInt())
        assertEquals(9, cutoff["minimum_generation_id"].asInt())
        assertEquals(42, cutoff["sync_id"].asInt())
        assertEquals(runId.toString(), cutoff["run_id"].asText())
        assertEquals(metadata.streamKey(stream), cutoff["stream_key"].asText())
        assertDoesNotThrow { UUID.fromString(cutoff["event_id"].asText()) }
        assertNotEquals(cutoff["event_id"].asText(), metadata.cutoff(stream)["event_id"])
        assertThrows(IllegalArgumentException::class.java) {
            metadata.cutoff(stream.copy(minimumGenerationId = 0))
        }
        listOf(-1L, 1L, 10L).forEach { minimum ->
            assertThrows(IllegalArgumentException::class.java) {
                metadata.descriptor(stream.copy(minimumGenerationId = minimum))
            }
            assertThrows(IllegalArgumentException::class.java) {
                metadata.cutoff(stream.copy(minimumGenerationId = minimum))
            }
        }
    }

    @Test
    fun `schema identifies CDC and rejects unsupported strategy or absent mappings`() {
        val stream =
            stream()
                .copy(
                    schema =
                        ObjectType(
                            linkedMapOf(
                                "_ab_cdc_deleted_at" to FieldType(TimestampTypeWithTimezone, true)
                            )
                        )
                )
        val descriptor = tree(metadata(stream).descriptor(stream))
        assertTrue(descriptor["layout"]["cdc"]["deleted_at_field_present"].asBoolean())
        assertEquals("HARD_DELETE", descriptor["layout"]["cdc"]["deletion_mode"].asText())
        val unsupported =
            BigqueryCopyMetadata(
                config,
                bigquery().copy(loadingMethod = BatchedStandardInsertConfiguration),
                names(stream),
                runId,
                DataChannelFormat.JSONL,
            )
        assertThrows(IllegalArgumentException::class.java) { unsupported.descriptor(stream) }
        val missing =
            BigqueryCopyMetadata(
                config,
                bigquery(),
                TableCatalogByDescriptor(emptyMap()),
                runId,
                DataChannelFormat.JSONL,
            )
        assertThrows(IllegalArgumentException::class.java) { missing.descriptor(stream) }
    }

    private fun stream() =
        DestinationStream(
            unmappedNamespace = "original_namespace",
            unmappedName = "Original Name",
            importType = Append,
            schema = schema,
            generationId = 9,
            minimumGenerationId = 0,
            syncId = 42,
            namespaceMapper = NamespaceMapper(),
        )

    private fun bigquery(raw: Boolean = false) =
        BigqueryConfiguration(
            projectId = "project",
            jobProjectId = "billing-project",
            datasetLocation = BigqueryRegion.US,
            datasetId = "default_dataset",
            loadingMethod = GcsStagingConfiguration(mockk(), GcsFilePostProcessing.KEEP),
            credentialsJson = null,
            cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            internalTableDataset = "raw_dataset",
            legacyRawTablesOnly = raw,
        )

    private fun names(stream: DestinationStream, mappingPrefix: String = "mapped_") =
        TableCatalogByDescriptor(
            mapOf(
                stream.mappedDescriptor to
                    TableNameInfo(
                        TableNames(
                            TableName("raw_dataset", "raw_table"),
                            TableName("mapped_dataset", "mapped_table"),
                        ),
                        ColumnNameMapping(
                            stream.schema
                                .asColumns()
                                .keys
                                .mapIndexed { i, name -> name to "$mappingPrefix$i" }
                                .toMap()
                        ),
                    )
            )
        )

    private fun metadata(
        stream: DestinationStream,
        raw: Boolean = false,
        format: DataChannelFormat = DataChannelFormat.JSONL,
        run: UUID = runId,
        mappingPrefix: String = "mapped_",
    ) = BigqueryCopyMetadata(config, bigquery(raw), names(stream, mappingPrefix), run, format)

    private fun tree(value: Map<String, Any?>): JsonNode =
        Jsons.readTree(metadata(stream()).serialize(value))

    private fun record(stream: DestinationStream, format: DataChannelFormat): DestinationRecordRaw {
        val source: DestinationRecordSource =
            if (format == DataChannelFormat.JSONL) {
                DestinationRecordJsonSource(
                    AirbyteMessage()
                        .withRecord(AirbyteRecordMessage().withEmittedAt(1234L).withData(payload))
                )
            } else {
                val encoder = AirbyteValueProtobufEncoder()
                val values =
                    stream.airbyteValueProxyFieldAccessors.map { accessor ->
                        val node = payload[accessor.name]
                        when (accessor.type) {
                            IntegerType ->
                                encoder.encode(node.asLong(), LeafAirbyteSchemaType.INTEGER)
                            TimestampTypeWithTimezone ->
                                encoder.encode(
                                    OffsetDateTime.parse(node.asText()),
                                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                                )
                            is ObjectType ->
                                encoder.encode(
                                    node.toString().toByteArray(Charsets.UTF_8),
                                    LeafAirbyteSchemaType.JSONB,
                                )
                            else ->
                                encoder.encode(
                                    node?.takeUnless { it.isNull }?.asText(),
                                    LeafAirbyteSchemaType.STRING,
                                )
                        }.build()
                    }
                DestinationRecordProtobufSource(
                    AirbyteMessageProtobuf.newBuilder()
                        .setRecord(
                            AirbyteRecordMessageProtobuf.newBuilder()
                                .setStreamName(stream.unmappedName)
                                .setEmittedAtMs(1234L)
                                .addAllData(values)
                        )
                        .build()
                )
            }
        return DestinationRecordRaw(stream, source, serializedSizeBytes = 123, airbyteRawId = runId)
    }
}

/** Real production formatter/compressor bytes reusable by the completed-GCS-object copy tests. */
internal fun bigqueryCopyFormattedGzip(
    stream: DestinationStream,
    config: BigqueryConfiguration,
    format: DataChannelFormat,
    record: DestinationRecordRaw,
): ByteArray {
    val bytes = ByteArrayOutputStream()
    BigQueryObjectStorageFormattingWriterFactory(config, format)
        .create(stream, GZIPOutputStream(bytes))
        .use { writer -> writer.accept(record) }
    return bytes.toByteArray()
}
