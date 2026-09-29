/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.google.protobuf.ByteString
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.stages.ParseStage
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.medium.JsonConverter
import io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter
import io.airbyte.cdk.load.file.ProtobufDataChannelReader
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteArrowBatchProtobuf
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import java.nio.channels.Channels
import org.apache.arrow.compression.CommonsCompressionFactory
import org.apache.arrow.memory.RootAllocator
import org.apache.arrow.vector.BigIntVector
import org.apache.arrow.vector.VarCharVector
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.VectorUnloader
import org.apache.arrow.vector.compression.CompressionUtil
import org.apache.arrow.vector.ipc.WriteChannel
import org.apache.arrow.vector.ipc.message.MessageSerializer
import org.apache.arrow.vector.types.pojo.ArrowType
import org.apache.arrow.vector.types.pojo.Field
import org.apache.arrow.vector.types.pojo.FieldType as ArrowFieldType
import org.apache.arrow.vector.types.pojo.Schema as ArrowSchema
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class ArrowBatchInputTest {
    private val stream =
        DestinationStream(
            unmappedNamespace = "arrow_namespace",
            unmappedName = "arrow_stream",
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 17,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                StreamTableSchema(
                    tableNames =
                        TableNames(finalTableName = TableName("arrow_namespace", "arrow_stream")),
                    columnSchema =
                        ColumnSchema(
                            inputSchema =
                                mapOf(
                                    "id" to FieldType(IntegerType, nullable = true),
                                    "name" to FieldType(StringType, nullable = true),
                                ),
                            inputToFinalColumnNames = mapOf("id" to "id", "name" to "name"),
                            finalSchema = emptyMap(),
                        ),
                    importType = Append,
                ),
        )

    @Test
    fun `protobuf reader creates a lazy Arrow batch with checkpoint and row count`() {
        val schemaBytes = ByteString.copyFromUtf8("ipc-schema")
        val batchBytes = ByteString.copyFromUtf8("ipc-record-batch")
        val input =
            AirbyteMessageProtobuf.newBuilder()
                .setArrowBatch(
                    AirbyteArrowBatchProtobuf.newBuilder()
                        .setStreamNamespace("arrow_namespace")
                        .setStreamName("arrow_stream")
                        .setEmittedAtMs(1234L)
                        .setPartitionId("read-stream-42")
                        .setRowCount(29)
                        .setArrowSchema(schemaBytes)
                        .setArrowRecordBatch(batchBytes)
                )
                .build()
        val delimited = ByteArrayOutputStream().apply { input.writeDelimitedTo(this) }
        val factory =
            DestinationMessageFactory(
                catalog = DestinationCatalog(listOf(stream)),
                dataChannelMedium = DataChannelMedium.SOCKET,
                namespaceMapper = NamespaceMapper(),
                uuidGenerator = UUIDGenerator(),
            )

        val message =
            ProtobufDataChannelReader(factory).read(delimited.toByteArray().inputStream()).single()
                as DestinationArrowBatch

        assertEquals(stream.mappedDescriptor, message.stream.mappedDescriptor)
        assertEquals(CheckpointId("read-stream-42"), message.checkpointId)
        assertEquals(29, message.rowCount)
        assertEquals(1234L, message.emittedAtMs)
        assertEquals(schemaBytes, message.schemaBytes)
        assertEquals(batchBytes, message.batchBytes)
        assertTrue(message.serializedSizeBytes > 0)
    }

    @Test
    fun `parse stage decodes a ZSTD compressed Arrow batch`() {
        val schema = testSchema()
        RootAllocator(Long.MAX_VALUE).use { allocator ->
            VectorSchemaRoot.create(schema, allocator).use { source ->
                source.allocateNew()
                val ids = source.getVector("id") as BigIntVector
                val names = source.getVector("name") as VarCharVector
                ids.setSafe(0, 10L)
                ids.setSafe(1, 20L)
                ids.setNull(2)
                names.setSafe(0, "one".toByteArray())
                names.setSafe(1, "café".toByteArray())
                names.setNull(2)
                source.rowCount = 3
                val expectedSizeBytes =
                    source.fieldVectors
                        .flatMap { it.fieldBuffers }
                        .sumOf { it.readableBytes().toLong() }

                val schemaOutput = ByteArrayOutputStream()
                MessageSerializer.serialize(WriteChannel(Channels.newChannel(schemaOutput)), schema)
                val codec =
                    CommonsCompressionFactory.INSTANCE.createCodec(
                        CompressionUtil.CodecType.ZSTD,
                    )
                val recordBatch = VectorUnloader(source, true, codec, true).recordBatch
                val batchOutput = ByteArrayOutputStream()
                try {
                    MessageSerializer.serialize(
                        WriteChannel(Channels.newChannel(batchOutput)),
                        recordBatch,
                    )
                } finally {
                    recordBatch.close()
                }
                val batch =
                    DestinationArrowBatch(
                        stream = stream,
                        checkpointId = CheckpointId("partition"),
                        rowCount = 3,
                        emittedAtMs = 999L,
                        schemaBytes = ByteString.copyFrom(schemaOutput.toByteArray()),
                        batchBytes = ByteString.copyFrom(batchOutput.toByteArray()),
                        serializedSizeBytes = 100L,
                    )
                val input =
                    DataFlowStageIO(
                        arrowBatch = batch,
                        partitionKey = PartitionKey("partition"),
                    )
                val stage = ParseStage(mockk<JsonConverter>(), mockk<ProtobufConverter>())

                val parsed =
                    kotlinx.coroutines.runBlocking { stage.apply(input) }.parsedArrowBatch!!
                try {
                    assertEquals(3, parsed.root.rowCount)
                    assertEquals(3, parsed.rowCount)
                    assertEquals(999L, parsed.emittedAtMs)
                    assertEquals(10L, (parsed.root.getVector("id") as BigIntVector).get(0))
                    assertEquals(20L, (parsed.root.getVector("id") as BigIntVector).get(1))
                    assertTrue((parsed.root.getVector("id") as BigIntVector).isNull(2))
                    assertEquals(
                        "café",
                        (parsed.root.getVector("name") as VarCharVector).getObject(1).toString()
                    )
                    assertEquals(expectedSizeBytes, parsed.sizeBytes)
                } finally {
                    parsed.root.close()
                }
            }
        }
    }

    private fun testSchema() =
        ArrowSchema(
            listOf(
                Field("id", ArrowFieldType.nullable(ArrowType.Int(64, true)), null),
                Field("name", ArrowFieldType.nullable(ArrowType.Utf8()), null),
            ),
        )
}
