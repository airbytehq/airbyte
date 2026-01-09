/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check.dlq

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.S3ObjectStorageConfig
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.BeanProvider
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.nio.file.Paths
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

/** DlqChecker helps actual connector perform a validation of the object storage configuration. */
@Singleton
class DlqChecker(private val objectStorageClientProvider: BeanProvider<ObjectStorageClient<*>>) {
    private val log = KotlinLogging.logger {}
    private val mockStream =
        DestinationStream(
            unmappedNamespace = "testing",
            unmappedName = "test",
            importType = Append,
            schema = ObjectTypeWithoutSchema,
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                StreamTableSchema(
                    tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                    columnSchema = ColumnSchema(mapOf(), mapOf(), mapOf()),
                    importType = Append,
                )
        )

    fun check(objectStorageConfig: ObjectStorageConfig) {
        when (objectStorageConfig) {
            is DisabledObjectStorageConfig -> {}
            is S3ObjectStorageConfig<*> -> writeTestBlob(objectStorageConfig)
        }
    }

    private fun <T> writeTestBlob(config: T) where
    T : ObjectStorageConfig,
    T : ObjectStoragePathConfigurationProvider,
    T : ObjectStorageFormatConfigurationProvider,
    T : ObjectStorageCompressionConfigurationProvider<*> {
        log.info { "Validating ${config.type} configuration for object storage" }

        val path = ObjectStoragePathFactory.from(config).getFinalDirectory(mockStream)
        val key = Paths.get(path, "_check_test").toString()
        log.info { "Checking if destination can write $key" }

        runBlocking {
            writeTestBlob(
                // We dynamically instantiate the client at this point because explicitly injecting
                // the client in the DlqChecker would fail when the dead letter queue is disabled.
                client = objectStorageClientProvider.get(),
                path = path,
                key = key,
                compressor = config.objectStorageCompressionConfiguration.compressor,
            )
        }
    }

    private suspend fun <T : RemoteObject<*>> writeTestBlob(
        client: ObjectStorageClient<T>,
        path: String,
        key: String,
        compressor: StreamProcessor<*>,
    ) {
        var remoteObject: T? = null
        try {
            val upload = client.startStreamingUpload(key)
            val byteStream = ByteArrayOutputStream()
            compressor.wrapper(byteStream).use { it.write("""{"data":1}""") }
            upload.uploadPart(byteStream.toByteArray(), 1)
            remoteObject = upload.complete()

            val results = client.list(path).toList()
            if (results.isEmpty() || results.find { it.key == key } == null) {
                throw IllegalStateException("Failed to write to the object storage")
            }
            log.info { "Successfully wrote test file: $results" }
        } finally {
            remoteObject?.let { client.delete(it) }
            log.info { "Successfully deleted test file" }
        }
    }
}
