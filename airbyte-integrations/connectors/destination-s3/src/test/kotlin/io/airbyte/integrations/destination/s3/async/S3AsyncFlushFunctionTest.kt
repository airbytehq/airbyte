package io.airbyte.integrations.destination.s3.async

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.WriteConfig
import io.airbyte.integrations.destination.s3.buffer.SerializedBufferFactory
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

@MicronautTest(environments = [Environment.TEST, "destination"], rebuildContext = true)
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "write")
@Property(name="${ConnectorConfigurationPropertySource.CONNECTOR_CATALOG_PREFIX}.${ConnectorConfigurationPropertySource.CONNECTOR_CATALOG_KEY}",
    value="{\"streams\":[{\"stream\":{\"name\":\"users\",\"namespace\":\"public\"},\"destination_sync_mode\":\"overwrite\"}]}")
class S3AsyncFlushFunctionTest {

    @Inject
    private lateinit var s3AsyncFlushFunction: S3AsyncFlushFunction
    private val amazonS3Client: AmazonS3 = mockk()
    private val serializedBufferFactory: SerializedBufferFactory = mockk()
    private val s3StorageOperations: S3StorageOperations = mockk()
    private val writeConfigGenerator: WriteConfigGenerator = mockk()

    @MockBean
    fun amazonS3Client(): AmazonS3 {
        return amazonS3Client
    }

    @Singleton
    @Primary
    fun serializedBufferFactory(): SerializedBufferFactory {
        return serializedBufferFactory
    }

    @Singleton
    @Primary
    fun s3StorageOperations(): S3StorageOperations {
        return s3StorageOperations
    }

    @Singleton
    @Primary
    fun writeConfigGenerator(): WriteConfigGenerator {
        return writeConfigGenerator
    }

    @Test
    internal fun `test that each partial message is written to the destination`() {
        val objectPath = "/test/output/path"
        val serializableBuffer: SerializableBuffer = mockk()
        val streamDescriptor = StreamDescriptor().withName("users").withNamespace("public")
        val partialMessages = generatePartialMessages(streamDescriptor)
        val writeConfigs = generateWriteConfigs(streamDescriptor, objectPath)

        every { serializableBuffer.accept(any(), any()) } returns 1L
        every { serializableBuffer.flush() } returns Unit
        every { serializableBuffer.byteCount } returns 1024L
        every { serializableBuffer.close() } returns Unit
        every { serializedBufferFactory.createSerializedBuffer(streamDescriptor) } returns serializableBuffer
        every { s3StorageOperations.uploadRecordsToBucket(serializableBuffer, streamDescriptor.namespace, objectPath) } returns objectPath
        every { writeConfigGenerator.toWriteConfigs() } returns writeConfigs

        s3AsyncFlushFunction.flush(streamDescriptor = streamDescriptor, stream = partialMessages.stream())

        verify(exactly = partialMessages.size) { serializableBuffer.accept(any(), any()) }
        verify(exactly = 1) { serializableBuffer.flush() }
        verify(exactly = 1) { s3StorageOperations.uploadRecordsToBucket(serializableBuffer, streamDescriptor.namespace, objectPath) }
        verify(exactly = 1) { serializableBuffer.close() }
    }

    @Test
    internal fun `test that each partial message is not written to the destination if the associated stream is not in the catalog`() {
        val objectPath = "/test/output/path"
        val serializableBuffer: SerializableBuffer = mockk()
        val streamDescriptor = StreamDescriptor().withName("users").withNamespace("public")
        val partialMessages = generatePartialMessages(streamDescriptor)
        val writeConfigs = generateWriteConfigs(StreamDescriptor().withName("other").withNamespace("other"), objectPath)

        every { serializableBuffer.accept(any(), any()) } returns 1L
        every { serializableBuffer.flush() } returns Unit
        every { serializableBuffer.byteCount } returns 1024L
        every { serializableBuffer.close() } returns Unit
        every { serializedBufferFactory.createSerializedBuffer(streamDescriptor) } returns serializableBuffer
        every { writeConfigGenerator.toWriteConfigs() } returns writeConfigs

        assertThrows<IllegalArgumentException> {
            s3AsyncFlushFunction.flush(streamDescriptor = streamDescriptor, stream = partialMessages.stream())
        }

        verify(exactly = partialMessages.size) { serializableBuffer.accept(any(), any()) }
        verify(exactly = 1) { serializableBuffer.flush() }
        verify(exactly = 1) { serializableBuffer.close() }
    }

    private fun generatePartialMessages(streamDescriptor: StreamDescriptor): List<PartialAirbyteMessage> {
        return List(5) {
            val jsonString = "{\"value\":$it}"
            val record = PartialAirbyteRecordMessage()
            record.stream = streamDescriptor.name
            record.namespace = streamDescriptor.namespace
            record.emittedAt = System.currentTimeMillis()
            record.data = Jsons.deserialize(jsonString)
            val message = PartialAirbyteMessage()
            message.record = record
            message.serialized = jsonString
            message.type = AirbyteMessage.Type.RECORD
            message
        }
    }

    private fun generateWriteConfigs(streamDescriptor: StreamDescriptor, objectPath: String): List<WriteConfig> {
        return List(5) {
            WriteConfig(streamDescriptor.namespace, streamDescriptor.name,
                objectPath, "pathFormat",
                objectPath, DestinationSyncMode.OVERWRITE)
        }
    }
}