package io.airbyte.integrations.destination.s3.async

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.WriteConfig
import io.airbyte.integrations.destination.s3.buffer.SerializedBufferFactory
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import org.apache.commons.io.FileUtils
import java.util.stream.Stream

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Named("destinationFlushFunction")
@Primary
class S3AsyncFlushFunction(
    private val serializedBufferFactory: SerializedBufferFactory,
    private val s3StorageOperations: S3StorageOperations,
    private val writeConfigGenerator: WriteConfigGenerator,
    @Value("\${airbyte.connector.async.optimal-batch-size-bytes}") private val optimalBatchSizeBytes: Long,
): DestinationFlushFunction {

    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        serializedBufferFactory.createSerializedBuffer(streamDescriptor).use { writer ->
            writeStreamToBufferStorage(streamDescriptor, stream, writer)
            val streamConfig = getStreamConfig(streamDescriptor)
            writeStreamToDestination(streamConfig, writer)
        }
    }

    override fun getOptimalBatchSizeBytes(): Long {
        return optimalBatchSizeBytes
    }

    @Throws(IllegalArgumentException::class)
    private fun getStreamConfig(streamDescriptor: StreamDescriptor): WriteConfig {
        val streamConfig = writeConfigGenerator.toWriteConfigs()
            .stream()
            .filter { StreamDescriptor().withName(it.streamName).withNamespace(it.namespace) == streamDescriptor }
            .findAny()
        require(streamConfig.isPresent) {
            "Message contained record from a stream that was not in the catalog."
        }
        return streamConfig.get()
    }

    private fun writeStreamToBufferStorage(
        streamDescriptor: StreamDescriptor,
        stream: Stream<PartialAirbyteMessage>,
        writer: SerializableBuffer
    ) {
        for(record in stream) {
            record.record?.let {
                writer.accept(record.serialized, it.emittedAt)
            }
        }

        writer.flush()
        logger.info { "Flushing buffer for stream ${streamDescriptor.name}:${streamDescriptor.namespace} (${FileUtils.byteCountToDisplaySize(writer.byteCount)}) to staging" }
    }

    private fun writeStreamToDestination(
        streamConfig: WriteConfig,
        writer: SerializableBuffer
    ) {
        s3StorageOperations.uploadRecordsToBucket(writer, streamConfig.namespace, streamConfig.fullOutputPath)
        logger.info { "Records successfully uploaded to path '${streamConfig.fullOutputPath}'."}
    }
}