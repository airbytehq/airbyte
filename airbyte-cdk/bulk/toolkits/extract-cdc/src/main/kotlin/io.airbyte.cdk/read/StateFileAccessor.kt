/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

/**
 * [StateFilesAccessor] reads and writes from Debezium offset and schema history files. This should
 * NOT be done while the Debezium Engine is running! None of this is thread-safe. Instead, this
 * object should be used to:
 * 1. create and populate the files prior to running the Debezium Engine,
 * 2. read the changed files after running the Debezium Engine.
 *
 * The files are deleted on [close].
 */
interface StateFilesAccessor {

    /*internal val workingDir: Path = Files.createTempDirectory(Path.of("/tmp"), DIRNAME_PREFIX)

    val offsetFilePath: Path = workingDir.resolve("offset.dat")
    val schemaFilePath: Path = workingDir.resolve("dbhistory.dat")

    private val fileOffsetBackingStore = FileOffsetBackingStore(keyConverter())

    init {
        val fileOffsetConfig =
            mapOf<String, String>(
                Pair(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter::class.java.name),
                Pair(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter::class.java.name),
                Pair(
                    StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG,
                    offsetFilePath.toString()
                ),
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

    fun readUpdatedOffset(oldOffset: DebeziumState.Offset): DebeziumState.Offset {
        val storeKeys = oldOffset.debeziumOffset.keys.map { k -> toBytes(k) }
        fileOffsetBackingStore.start()
        val future = fileOffsetBackingStore.get(storeKeys)
        val newOffset = future.get().map { (k, v) -> Pair(toJson(k), toJson(v)) }.toMap()
        fileOffsetBackingStore.stop()
        return DebeziumState.Offset(newOffset)
    }

    fun writeOffset(offset: DebeziumState.Offset) {
        val storeMap = offset.debeziumOffset.map { (k, v) -> Pair(toBytes(k), toBytes(v)) }.toMap()
        fileOffsetBackingStore.start()
        fileOffsetBackingStore.set(storeMap, null)
        fileOffsetBackingStore.stop()
    }

    fun readSchema(): DebeziumState.Schema {
        fileSchemaHistory.start()
        val schema: List<HistoryRecord> = buildList {
            recoverRecords(fileSchemaHistory, Consumer(this::add))
        }
        fileSchemaHistory.stop()
        return DebeziumState.Schema(schema)
    }

    fun writeSchema(schema: DebeziumState.Schema) {
        fileSchemaHistory.initializeStorage()
        fileSchemaHistory.start()
        for (r in schema.debeziumSchemaHistory) {
            storeRecord(fileSchemaHistory, r)
        }
        fileSchemaHistory.stop()
    }

    private fun toJson(byteBuffer: ByteBuffer): JsonNode {
        val bytes = ByteArray(byteBuffer.remaining())
        byteBuffer.asReadOnlyBuffer().get(bytes)
        return Jsons.deserializeExact(bytes)
    }

    private fun toBytes(json: JsonNode): ByteBuffer = ByteBuffer.wrap(Jsons.toBytes(json))

    private fun keyConverter(): Converter {
        val converter = JsonConverter()
        val config = mapOf(Pair(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString()))
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
    }*/
}
