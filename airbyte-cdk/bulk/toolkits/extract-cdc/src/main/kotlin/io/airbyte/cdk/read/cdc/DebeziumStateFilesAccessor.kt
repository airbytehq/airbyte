/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.debezium.config.Configuration
import io.debezium.relational.history.AbstractFileBasedSchemaHistory
import io.debezium.relational.history.HistoryRecord
import io.debezium.relational.history.HistoryRecordComparator
import io.debezium.relational.history.SchemaHistoryListener
import io.debezium.storage.file.history.FileSchemaHistory
import java.lang.reflect.Method
import java.nio.ByteBuffer
import java.nio.file.Files
import java.nio.file.Path
import java.util.function.Consumer
import kotlin.String
import org.apache.commons.io.FileUtils
import org.apache.kafka.connect.json.JsonConverter
import org.apache.kafka.connect.json.JsonConverterConfig
import org.apache.kafka.connect.runtime.WorkerConfig
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.storage.Converter
import org.apache.kafka.connect.storage.FileOffsetBackingStore

/**
 * [DebeziumStateFilesAccessor] reads and writes from Debezium offset and schema history files. This
 * should NOT be done while the Debezium Engine is running! None of this is thread-safe. Instead,
 * this object should be used to:
 * 1. create and populate the files prior to running the Debezium Engine,
 * 2. read the changed files after running the Debezium Engine.
 *
 * The files are deleted on [close].
 */
class DebeziumStateFilesAccessor : AutoCloseable {

    internal val workingDir: Path = Files.createTempDirectory(Path.of("/tmp"), DIRNAME_PREFIX)

    val offsetFilePath: Path = workingDir.resolve("offset.dat")
    val schemaFilePath: Path = workingDir.resolve("dbhistory.dat")

    private val fileOffsetBackingStore = FileOffsetBackingStore(keyConverter())

    init {
        val fileOffsetConfig =
            mapOf<String, String>(
                WorkerConfig.KEY_CONVERTER_CLASS_CONFIG to JsonConverter::class.java.name,
                WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG to JsonConverter::class.java.name,
                StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG to offsetFilePath.toString(),
            )
        fileOffsetBackingStore.configure(StandaloneConfig(fileOffsetConfig))
    }

    private val fileSchemaHistory = FileSchemaHistory()

    init {
        fileSchemaHistory.configure(
            Configuration.create()
                .with(FileSchemaHistory.FILE_PATH, schemaFilePath.toString())
                .build(),
            HistoryRecordComparator.INSTANCE,
            SchemaHistoryListener.NOOP,
            false
        )
    }

    override fun close() {
        fileOffsetBackingStore.stop()
        fileSchemaHistory.stop()
        FileUtils.deleteDirectory(workingDir.toFile())
    }

    fun readUpdatedOffset(oldOffset: DebeziumOffset): DebeziumOffset {
        val storeKeys = oldOffset.wrapped.keys.map { k -> toBytes(k) }
        fileOffsetBackingStore.start()
        val byteBufferMap: Map<ByteBuffer, ByteBuffer> = fileOffsetBackingStore.get(storeKeys).get()
        val newOffset: Map<JsonNode, JsonNode> =
            byteBufferMap.map { (k, v) -> toJson(k) to toJson(v) }.toMap()
        fileOffsetBackingStore.stop()
        return DebeziumOffset(newOffset)
    }

    fun writeOffset(offset: DebeziumOffset) {
        val storeMap = offset.wrapped.map { (k, v) -> toBytes(k) to toBytes(v) }.toMap()
        fileOffsetBackingStore.start()
        fileOffsetBackingStore.set(storeMap, null)
        fileOffsetBackingStore.stop()
    }

    fun readSchema(): DebeziumSchemaHistory {
        fileSchemaHistory.start()
        val schema: List<HistoryRecord> = buildList {
            recoverRecords(fileSchemaHistory, Consumer(this::add))
        }
        fileSchemaHistory.stop()
        return DebeziumSchemaHistory(schema)
    }

    fun writeSchema(schema: DebeziumSchemaHistory) {
        fileSchemaHistory.initializeStorage()
        fileSchemaHistory.start()
        for (r in schema.wrapped) {
            storeRecord(fileSchemaHistory, r)
        }
        fileSchemaHistory.stop()
    }

    private fun toJson(byteBuffer: ByteBuffer): JsonNode {
        val bytes = ByteArray(byteBuffer.remaining())
        byteBuffer.asReadOnlyBuffer().get(bytes)
        return Jsons.readTree(bytes)
    }

    private fun toBytes(json: JsonNode): ByteBuffer = ByteBuffer.wrap(Jsons.writeValueAsBytes(json))

    private fun keyConverter(): Converter {
        val converter = JsonConverter()
        val config = mapOf(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG to false.toString())
        converter.configure(config, true)
        return converter
    }

    companion object {
        private const val DIRNAME_PREFIX = "airbyte-debezium-state"

        // Use reflection to access the necessary protected methods in FileSchemaHistory.
        private val storeRecord: Method =
            AbstractFileBasedSchemaHistory::class
                .java
                .getDeclaredMethod("storeRecord", HistoryRecord::class.java)
                .apply { isAccessible = true }

        private val recoverRecords: Method =
            AbstractFileBasedSchemaHistory::class
                .java
                .getDeclaredMethod("recoverRecords", Consumer::class.java)
                .apply { isAccessible = true }
    }
}
