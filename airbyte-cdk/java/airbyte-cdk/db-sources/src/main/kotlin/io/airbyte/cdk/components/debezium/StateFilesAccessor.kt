/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.collect.ImmutableList
import io.airbyte.commons.jackson.MoreMappers
import io.debezium.config.Configuration
import io.debezium.relational.history.AbstractFileBasedSchemaHistory
import io.debezium.relational.history.HistoryRecord
import io.debezium.relational.history.HistoryRecordComparator
import io.debezium.relational.history.SchemaHistoryListener
import io.debezium.storage.file.history.FileSchemaHistory
import org.apache.commons.io.FileUtils
import org.apache.kafka.common.utils.ByteBufferInputStream
import org.apache.kafka.connect.json.JsonConverter
import org.apache.kafka.connect.json.JsonConverterConfig
import org.apache.kafka.connect.runtime.WorkerConfig
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.storage.Converter
import org.apache.kafka.connect.storage.FileOffsetBackingStore
import java.io.IOException
import java.io.UncheckedIOException
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method
import java.nio.ByteBuffer
import java.nio.file.Files
import java.nio.file.Path
import java.util.function.Consumer
import kotlin.Exception
import kotlin.RuntimeException
import kotlin.String

class StateFilesAccessor : AutoCloseable {

    val offsetFilePath: Path
    val schemaFilePath: Path

    internal val workingDir: Path
    private val fileOffsetBackingStore: FileOffsetBackingStore
    private val fileSchemaHistory: FileSchemaHistory

    override fun close() {
        fileOffsetBackingStore.stop()
        fileSchemaHistory.stop()
        try {
            FileUtils.deleteDirectory(workingDir.toFile())
        } catch (e: IOException) {
            throw UncheckedIOException(e)
        }
    }

    fun readUpdatedOffset(offset: DebeziumComponent.State.Offset): DebeziumComponent.State.Offset {
        val bytesKeys = offset.debeziumOffset.keys.map { key -> toByteBuffer(key) }
        fileOffsetBackingStore.start()
        val future = fileOffsetBackingStore.get(bytesKeys)
        fileOffsetBackingStore.stop()
        val debeziumOffset = future.resultNow()
                .map { (key, value) -> Pair(toJson(key), toJson(value)) }
                .toMap()
        return DebeziumComponent.State.Offset(debeziumOffset)
    }

    fun writeOffset(offset: DebeziumComponent.State.Offset) {
        val bytesMap = offset.debeziumOffset.map { (key, value) -> Pair(toByteBuffer(key), toByteBuffer(value)) }.toMap()
        fileOffsetBackingStore.start()
        fileOffsetBackingStore.set(bytesMap, null)
        fileOffsetBackingStore.stop()
    }

    fun readSchema(): DebeziumComponent.State.Schema {
        val builder = ImmutableList.builder<HistoryRecord>()
        val consumer = Consumer { element: HistoryRecord -> builder.add(element) }
        fileSchemaHistory.start()
        try {
            RECOVER_RECORDS_METHOD.invoke(fileSchemaHistory, consumer)
        } catch (e: IllegalAccessException) {
            throw RuntimeException(e)
        } catch (e: InvocationTargetException) {
            throw RuntimeException(e)
        }
        fileSchemaHistory.stop()
        return DebeziumComponent.State.Schema(builder.build())
    }

    fun writeSchema(schema: DebeziumComponent.State.Schema) {
        fileSchemaHistory.initializeStorage()
        fileSchemaHistory.start()
        for (r in schema.debeziumSchemaHistory) {
            try {
                STORE_RECORD_METHOD.invoke(fileSchemaHistory, r)
            } catch (e: IllegalAccessException) {
                throw RuntimeException(e)
            } catch (e: InvocationTargetException) {
                throw RuntimeException(e)
            }
        }
        fileSchemaHistory.stop()
    }

    init {
        try {
            workingDir = Files.createTempDirectory(Path.of("/tmp"), "airbyte-debezium-state")
        } catch (e: IOException) {
            throw UncheckedIOException(e)
        }
        offsetFilePath = workingDir.resolve("offset.dat")
        schemaFilePath = workingDir.resolve("dbhistory.dat")
        // Create and configure FileOffsetBackingStore instance.
        fileOffsetBackingStore = FileOffsetBackingStore(keyConverter())
        val offsetProps = HashMap<String, String>()
        offsetProps[WorkerConfig.KEY_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        offsetProps[WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        offsetProps[StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG] = offsetFilePath.toString()
        fileOffsetBackingStore.configure(StandaloneConfig(offsetProps))
        // Create and configure FileSchemaHistory instance.
        fileSchemaHistory = FileSchemaHistory()
        val schemaConfig = Configuration.create()
                .with(FileSchemaHistory.FILE_PATH, schemaFilePath.toString())
                .build()
        fileSchemaHistory.configure(schemaConfig, HistoryRecordComparator.INSTANCE, SchemaHistoryListener.NOOP, false)
    }

    companion object {
        // Use reflection to access the necessary protected methods in FileSchemaHistory.
        private val STORE_RECORD_METHOD: Method
        private val RECOVER_RECORDS_METHOD: Method

        init {
            try {
                STORE_RECORD_METHOD = AbstractFileBasedSchemaHistory::class.java.getDeclaredMethod("storeRecord", HistoryRecord::class.java)
                RECOVER_RECORDS_METHOD = AbstractFileBasedSchemaHistory::class.java.getDeclaredMethod("recoverRecords", Consumer::class.java)
            } catch (e: NoSuchMethodException) {
                throw RuntimeException(e)
            }
            STORE_RECORD_METHOD.setAccessible(true)
            RECOVER_RECORDS_METHOD.setAccessible(true)
        }

        private fun keyConverter(): Converter {
            val converter = JsonConverter()
            val converterConfig = mapOf(Pair(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString()))
            converter.configure(converterConfig, true)
            return converter
        }

        private fun toJson(byteBuffer: ByteBuffer): JsonNode {
            try {
                return OBJECT_MAPPER.readTree(ByteBufferInputStream(byteBuffer.asReadOnlyBuffer()))
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        private fun toByteBuffer(json: JsonNode): ByteBuffer {
            try {
                return ByteBuffer.wrap(OBJECT_MAPPER.writeValueAsBytes(json))
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        private val OBJECT_MAPPER: ObjectMapper = MoreMappers.initMapper()
    }
}
