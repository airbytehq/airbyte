/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.dataflow.transform.medium.ConversionInput
import io.airbyte.cdk.load.dataflow.transform.medium.JsonConverter
import io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter
import io.airbyte.cdk.load.message.ArrowBatchDTO
import io.airbyte.cdk.load.message.DestinationArrowBatch
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Named
import jakarta.inject.Singleton
import org.apache.arrow.compression.CommonsCompressionFactory
import org.apache.arrow.memory.RootAllocator
import org.apache.arrow.vector.VectorLoader
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.ipc.ReadChannel
import org.apache.arrow.vector.ipc.message.ArrowRecordBatch
import org.apache.arrow.vector.ipc.message.MessageSerializer
import org.apache.arrow.vector.util.ByteArrayReadableSeekableByteChannel

@Named("parse")
@Singleton
class ParseStage(
    private val jsonConverter: JsonConverter,
    private val protobufConverter: ProtobufConverter
) : DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        input.arrowBatch?.let { batch ->
            val root = decode(batch)
            val sizeBytes =
                root.fieldVectors.flatMap { it.fieldBuffers }.sumOf { it.readableBytes().toLong() }
            return input.apply {
                parsedArrowBatch =
                    ArrowBatchDTO(
                        root = root,
                        partitionKey = input.partitionKey!!,
                        rowCount = batch.rowCount,
                        sizeBytes = sizeBytes,
                        emittedAtMs = batch.emittedAtMs,
                    )
            }
        }
        val raw = input.raw!!
        val fields = transform(raw, input.partitionKey!!)
        return input.apply {
            munged =
                RecordDTO(
                    fields = fields,
                    partitionKey = input.partitionKey!!,
                    sizeBytes = raw.serializedSizeBytes,
                    emittedAtMs = raw.rawData.emittedAtMs,
                )
        }
    }

    private fun decode(batch: DestinationArrowBatch): VectorSchemaRoot {
        val allocator = ArrowMemory.allocator
        val schema =
            MessageSerializer.deserializeSchema(
                ReadChannel(ByteArrayReadableSeekableByteChannel(batch.schemaBytes.toByteArray()))
            )
        val root = VectorSchemaRoot.create(schema, allocator)
        try {
            val recordBatch: ArrowRecordBatch =
                MessageSerializer.deserializeRecordBatch(
                    ReadChannel(
                        ByteArrayReadableSeekableByteChannel(batch.batchBytes.toByteArray())
                    ),
                    allocator,
                )
            try {
                VectorLoader(root, CommonsCompressionFactory.INSTANCE).load(recordBatch)
            } finally {
                recordBatch.close()
            }
            check(root.rowCount == batch.rowCount) {
                "Arrow batch row count mismatch: declared ${batch.rowCount}, decoded ${root.rowCount}"
            }
            return root
        } catch (e: Throwable) {
            root.close()
            throw e
        }
    }

    private fun transform(
        msg: DestinationRecordRaw,
        partitionKey: PartitionKey
    ): Map<String, AirbyteValue> {
        val input = ConversionInput(msg = msg, partitionKey = partitionKey)
        return when (msg.rawData) {
            is DestinationRecordProtobufSource -> protobufConverter.convert(input)
            else -> jsonConverter.convert(input)
        }
    }
}

private object ArrowMemory {
    val allocator = RootAllocator(Long.MAX_VALUE)
}
