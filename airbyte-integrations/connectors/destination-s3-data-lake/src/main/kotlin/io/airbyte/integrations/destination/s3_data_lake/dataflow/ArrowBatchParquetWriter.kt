/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ArrowBatchDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.UUIDGenerator
import java.math.BigDecimal
import java.math.BigInteger
import java.util.stream.Stream
import org.apache.arrow.vector.BigIntVector
import org.apache.arrow.vector.BitVector
import org.apache.arrow.vector.DateDayVector
import org.apache.arrow.vector.DecimalVector
import org.apache.arrow.vector.FieldVector
import org.apache.arrow.vector.Float8Vector
import org.apache.arrow.vector.LargeVarCharVector
import org.apache.arrow.vector.TimeStampMicroTZVector
import org.apache.arrow.vector.TimeStampMicroVector
import org.apache.arrow.vector.VarCharVector
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.iceberg.DataFile
import org.apache.iceberg.DataFiles
import org.apache.iceberg.FieldMetrics
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
import org.apache.iceberg.io.FileAppender
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.parquet.ParquetValueWriter
import org.apache.iceberg.parquet.ParquetValueWriters
import org.apache.iceberg.parquet.TripleWriter
import org.apache.iceberg.util.PropertyUtil
import org.apache.parquet.column.ColumnDescriptor
import org.apache.parquet.column.ColumnWriteStore
import org.apache.parquet.io.api.Binary
import org.apache.parquet.schema.GroupType
import org.apache.parquet.schema.MessageType
import org.apache.parquet.schema.Type.Repetition

class ArrowBatchParquetWriter(
    private val messageType: MessageType,
    private val stream: DestinationStream,
    private val schema: org.apache.iceberg.Schema,
    private val uuidGenerator: UUIDGenerator,
) : ParquetValueWriter<Int> {
    private val inputNameByFinalName =
        stream.tableSchema.columnSchema.inputToFinalColumnNames.entries.associate {
            it.value to it.key
        }
    private val columns =
        messageType.columns.map { descriptor ->
            val path = descriptor.path
            val baseWriter = baseWriter(descriptor)
            ArrowColumnWriter(
                descriptor = descriptor,
                path = path,
                baseWriter = baseWriter,
                tripleWriter = baseWriter.columns().single(),
                icebergType =
                    if (path.firstOrNull() in Meta.COLUMN_NAMES) {
                        null
                    } else {
                        schema.findField(path[0])?.type()
                            ?: throw UnsupportedOperationException(
                                "Arrow field ${path[0]} is missing from the Iceberg schema"
                            )
                    },
                emptyListDefinitionLevel =
                    if (
                        path.firstOrNull() == Meta.COLUMN_NAME_AB_META &&
                            path.getOrNull(1) == Meta.AIRBYTE_META_CHANGES
                    ) {
                        emptyListDefinitionLevel(messageType, path)
                    } else {
                        null
                    },
            )
        }

    private var root: VectorSchemaRoot? = null
    private var emittedAtMs: Long = 0
    private var vectorsByName: Map<String, FieldVector> = emptyMap()

    fun setBatch(batch: ArrowBatchDTO) {
        root = batch.root
        emittedAtMs = batch.emittedAtMs
        vectorsByName = batch.root.fieldVectors.associateBy { it.name }
        val declaredSourceFields = stream.tableSchema.columnSchema.inputSchema.keys
        val unexpectedFields = vectorsByName.keys - declaredSourceFields
        require(unexpectedFields.isEmpty()) {
            "ARROW schema evolution is unsupported; unexpected fields: ${unexpectedFields.sorted()}"
        }
        schema
            .columns()
            .filterNot { it.name() in Meta.COLUMN_NAMES }
            .forEach { field ->
                val sourceName = inputNameByFinalName[field.name()] ?: field.name()
                val vector = vectorsByName[sourceName]
                if (vector != null) {
                    requireSupportedPair(field.type(), vector)
                } else {
                    requireSupportedIcebergType(field.type(), field.name())
                }
            }
    }

    override fun write(repetitionLevel: Int, rowIndex: Int) {
        requireNotNull(root) { "No Arrow batch set on Parquet writer" }
        columns.forEach { it.write(repetitionLevel, rowIndex, vectorsByName) }
    }

    override fun columns(): List<TripleWriter<*>> = columns.map { it.tripleWriter }

    override fun setColumnStore(columnStore: ColumnWriteStore) {
        columns.forEach { it.baseWriter.setColumnStore(columnStore) }
    }

    override fun metrics(): Stream<FieldMetrics<*>> =
        columns.flatMap { it.baseWriter.metrics().toList() }.stream()

    private fun baseWriter(descriptor: ColumnDescriptor): ParquetValueWriter<*> {
        return when (descriptor.primitiveType.primitiveTypeName) {
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.BOOLEAN ->
                ParquetValueWriters.booleans(descriptor)
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT32 ->
                ParquetValueWriters.ints(descriptor)
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT64 ->
                ParquetValueWriters.longs(descriptor)
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.DOUBLE ->
                ParquetValueWriters.doubles(descriptor)
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.BINARY,
            org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.FIXED_LEN_BYTE_ARRAY ->
                ParquetValueWriters.byteBuffers(descriptor)
            else ->
                throw UnsupportedOperationException(
                    "Unsupported Parquet primitive ${descriptor.primitiveType.primitiveTypeName} for Arrow batches"
                )
        }
    }

    private inner class ArrowColumnWriter(
        val descriptor: ColumnDescriptor,
        val path: Array<String>,
        val baseWriter: ParquetValueWriter<*>,
        val tripleWriter: TripleWriter<*>,
        val icebergType: org.apache.iceberg.types.Type?,
        val emptyListDefinitionLevel: Int?,
    ) {
        fun write(
            repetitionLevel: Int,
            rowIndex: Int,
            vectors: Map<String, FieldVector>,
        ) {
            when (path.first()) {
                Meta.COLUMN_NAME_AB_RAW_ID -> {
                    tripleWriter.writeBinary(
                        repetitionLevel,
                        Binary.fromString(uuidGenerator.v7().toString())
                    )
                    return
                }
                Meta.COLUMN_NAME_AB_EXTRACTED_AT -> {
                    tripleWriter.writeLong(repetitionLevel, emittedAtMs)
                    return
                }
                Meta.COLUMN_NAME_AB_GENERATION_ID -> {
                    tripleWriter.writeLong(repetitionLevel, stream.generationId)
                    return
                }
                Meta.COLUMN_NAME_AB_META -> {
                    when (path.getOrNull(1)) {
                        Meta.AIRBYTE_META_SYNC_ID ->
                            tripleWriter.writeLong(repetitionLevel, stream.syncId)
                        Meta.AIRBYTE_META_CHANGES ->
                            tripleWriter.writeNull(
                                repetitionLevel,
                                requireNotNull(emptyListDefinitionLevel),
                            )
                        else ->
                            throw UnsupportedOperationException(
                                "Unsupported _airbyte_meta Arrow field ${path.joinToString(".")}"
                            )
                    }
                    return
                }
            }

            if (path.size != 1) {
                throw UnsupportedOperationException(
                    "Nested Arrow field ${path.joinToString(".")} is not supported"
                )
            }
            val sourceName = inputNameByFinalName[path[0]] ?: path[0]
            val vector = vectors[sourceName]
            if (vector == null || vector.isNull(rowIndex)) {
                require(descriptor.maxDefinitionLevel > 0) {
                    "ARROW cannot write null to required Iceberg field ${path.joinToString(".")}"
                }
                tripleWriter.writeNull(repetitionLevel, descriptor.maxDefinitionLevel - 1)
                return
            }

            when (vector) {
                is BigIntVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.LONG,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT64,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeLong(repetitionLevel, vector.get(rowIndex))
                }
                is VarCharVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.STRING,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.BINARY,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeBinary(
                        repetitionLevel,
                        vector
                            .getDataBuffer()
                            .asBinary(
                                vector
                                    .getOffsetBuffer()
                                    .getInt(rowIndex.toLong() * Int.SIZE_BYTES)
                                    .toLong(),
                                vector
                                    .getOffsetBuffer()
                                    .getInt((rowIndex + 1).toLong() * Int.SIZE_BYTES)
                                    .toLong(),
                            ),
                    )
                }
                is LargeVarCharVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.STRING,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.BINARY,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeBinary(
                        repetitionLevel,
                        vector
                            .getDataBuffer()
                            .asBinary(
                                vector
                                    .getOffsetBuffer()
                                    .getLong(rowIndex.toLong() * Long.SIZE_BYTES),
                                vector
                                    .getOffsetBuffer()
                                    .getLong((rowIndex + 1).toLong() * Long.SIZE_BYTES),
                            ),
                    )
                }
                is Float8Vector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.DOUBLE,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.DOUBLE,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeDouble(repetitionLevel, vector.get(rowIndex))
                }
                is DecimalVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.DOUBLE,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.DOUBLE,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeDouble(
                        repetitionLevel,
                        vector.getObject(rowIndex).asDouble(),
                    )
                }
                is BitVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.BOOLEAN,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.BOOLEAN,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeBoolean(repetitionLevel, vector.get(rowIndex) != 0)
                }
                is DateDayVector -> {
                    requireIcebergType(
                        org.apache.iceberg.types.Type.TypeID.DATE,
                        vector.javaClass.simpleName
                    )
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT32,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeInteger(repetitionLevel, vector.get(rowIndex))
                }
                is TimeStampMicroVector -> {
                    requireTimestampType(vector.javaClass.simpleName, withZone = false)
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT64,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeLong(repetitionLevel, vector.get(rowIndex))
                }
                is TimeStampMicroTZVector -> {
                    requireTimestampType(vector.javaClass.simpleName, withZone = true)
                    requireParquetType(
                        org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName.INT64,
                        vector.javaClass.simpleName,
                    )
                    tripleWriter.writeLong(repetitionLevel, vector.get(rowIndex))
                }
                else ->
                    throw UnsupportedOperationException(
                        "Unsupported Arrow vector ${vector.javaClass.simpleName} for ${path.joinToString(".")}"
                    )
            }
        }

        private fun requireParquetType(
            expected: org.apache.parquet.schema.PrimitiveType.PrimitiveTypeName,
            arrowType: String,
        ) {
            require(descriptor.primitiveType.primitiveTypeName == expected) {
                "Unsupported Arrow/Parquet type pair $arrowType and ${descriptor.primitiveType.primitiveTypeName} for ${path.joinToString(".")}"
            }
        }

        private fun requireIcebergType(
            expected: org.apache.iceberg.types.Type.TypeID,
            arrowType: String
        ) {
            require(icebergType?.typeId() == expected) {
                "Unsupported Arrow/Iceberg type pair $arrowType and ${icebergType?.typeId()} for ${path.joinToString(".")}"
            }
        }

        private fun requireTimestampType(arrowType: String, withZone: Boolean) {
            val timestampType = icebergType as? org.apache.iceberg.types.Types.TimestampType
            require(timestampType != null && timestampType.shouldAdjustToUTC() == withZone) {
                "Unsupported Arrow/Iceberg type pair $arrowType and ${icebergType?.typeId()} for ${path.joinToString(".")}"
            }
        }
    }

    private fun requireSupportedIcebergType(type: org.apache.iceberg.types.Type, name: String) {
        require(
            type.typeId() in
                setOf(
                    org.apache.iceberg.types.Type.TypeID.LONG,
                    org.apache.iceberg.types.Type.TypeID.STRING,
                    org.apache.iceberg.types.Type.TypeID.DOUBLE,
                    org.apache.iceberg.types.Type.TypeID.BOOLEAN,
                    org.apache.iceberg.types.Type.TypeID.DATE,
                    org.apache.iceberg.types.Type.TypeID.TIMESTAMP,
                ),
        ) {
            "Unsupported Iceberg type ${type.typeId()} for Arrow field $name"
        }
    }

    private fun requireSupportedPair(type: org.apache.iceberg.types.Type, vector: FieldVector) {
        requireSupportedIcebergType(type, vector.name)
        val supported =
            when (vector) {
                is BigIntVector -> type.typeId() == org.apache.iceberg.types.Type.TypeID.LONG
                is VarCharVector,
                is LargeVarCharVector ->
                    type.typeId() == org.apache.iceberg.types.Type.TypeID.STRING
                is Float8Vector,
                is DecimalVector -> type.typeId() == org.apache.iceberg.types.Type.TypeID.DOUBLE
                is BitVector -> type.typeId() == org.apache.iceberg.types.Type.TypeID.BOOLEAN
                is DateDayVector -> type.typeId() == org.apache.iceberg.types.Type.TypeID.DATE
                is TimeStampMicroVector ->
                    type is org.apache.iceberg.types.Types.TimestampType &&
                        !type.shouldAdjustToUTC()
                is TimeStampMicroTZVector ->
                    type is org.apache.iceberg.types.Types.TimestampType && type.shouldAdjustToUTC()
                else -> false
            }
        require(supported) {
            "Unsupported Arrow/Iceberg type pair ${vector.javaClass.simpleName} and ${type.typeId()} for ${vector.name}"
        }
    }

    private fun BigDecimal.asDouble(): Double {
        val unscaled = unscaledValue()
        val scale = scale()
        val limit = BigInteger.ONE.shiftLeft(53)
        return if (unscaled.abs() <= limit && scale in 0..15) {
            unscaled.toLong().toDouble() / Math.pow(10.0, scale.toDouble())
        } else {
            toDouble()
        }
    }

    private fun org.apache.arrow.memory.ArrowBuf.asBinary(start: Long, end: Long): Binary {
        val length = Math.toIntExact(end - start)
        return Binary.fromReusedByteBuffer(nioBuffer(start, length))
    }

    private fun emptyListDefinitionLevel(messageType: MessageType, path: Array<String>): Int {
        var group: GroupType = messageType
        var definitionLevel = 0
        for (name in path) {
            val type = group.getType(name)
            if (type.repetition != Repetition.REQUIRED) {
                definitionLevel++
            }
            if (type.repetition == Repetition.REPEATED) {
                return definitionLevel - 1
            }
            if (!type.isPrimitive) {
                group = type.asGroupType()
            }
        }
        throw IllegalArgumentException("Expected repeated list field at ${path.joinToString(".")}")
    }
}

class ArrowBatchFileWriter(
    private val table: Table,
    private val stream: DestinationStream,
    private val uuidGenerator: UUIDGenerator = UUIDGenerator(),
) : AutoCloseable {
    private val targetFileSize =
        PropertyUtil.propertyAsLong(
            table.properties(),
            WRITE_TARGET_FILE_SIZE_BYTES,
            WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT,
        )
    private val completedFiles = mutableListOf<DataFile>()
    private var currentAppender: FileAppender<Int>? = null
    private var currentPath: String? = null
    private var currentWriter: ArrowBatchParquetWriter? = null
    private var closed = false

    fun write(batch: ArrowBatchDTO) {
        check(!closed) { "Arrow batch writer is closed" }
        val root = batch.root
        if (root.rowCount == 0) {
            return
        }
        ensureAppender()
        currentWriter!!.setBatch(batch)
        for (rowIndex in 0 until root.rowCount) {
            currentAppender!!.add(rowIndex)
            if (currentAppender!!.length() >= targetFileSize) {
                if (rowIndex < root.rowCount - 1) {
                    closeCurrentAppender()
                    ensureAppender()
                    currentWriter!!.setBatch(batch)
                } else {
                    closeCurrentAppender()
                }
            }
        }
    }

    fun complete(): List<DataFile> {
        if (!closed) {
            closeCurrentAppender()
            closed = true
        }
        return completedFiles.toList()
    }

    override fun close() {
        complete()
    }

    private fun ensureAppender() {
        if (currentAppender != null) {
            return
        }
        val filename = "${uuidGenerator.v7()}.parquet"
        val path = table.locationProvider().newDataLocation(filename)
        currentPath = path
        var writer: ArrowBatchParquetWriter? = null
        currentAppender =
            Parquet.write(table.io().newOutputFile(path))
                .forTable(table)
                .createWriterFunc { messageType ->
                    ArrowBatchParquetWriter(messageType, stream, table.schema(), uuidGenerator)
                        .also { writer = it }
                }
                .build()
        currentWriter = requireNotNull(writer)
    }

    private fun closeCurrentAppender() {
        val appender = currentAppender ?: return
        appender.close()
        val metrics = appender.metrics()
        completedFiles.add(
            DataFiles.builder(table.spec())
                .withPath(requireNotNull(currentPath))
                .withFormat(FileFormat.PARQUET)
                .withFileSizeInBytes(appender.length())
                .withRecordCount(metrics.recordCount())
                .withMetrics(metrics)
                .build(),
        )
        currentAppender = null
        currentPath = null
        currentWriter = null
    }
}
