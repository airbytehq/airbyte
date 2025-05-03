/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.SocketTestConfig
import io.airbyte.cdk.load.file.SocketInputFlow
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageDirectLoadOverride
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoaderFactory
import jakarta.inject.Named
import javax.inject.Singleton

@Singleton
class AzureBlobStorageWriter(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<AzureBlob, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}

@Singleton
class AzureBlobStorageDirectLoadOverride(
    @Named("socketInputFlows") private val socketInputFlows: Array<SocketInputFlow>,
    private val writerFactory: BufferedFormattingWriterFactory<*>,
    private val catalog: DestinationCatalog,
    private val config: SocketTestConfig,
    private val client: ObjectStorageClient<*>,
    private val pathFactory: ObjectStoragePathFactory,
): ObjectStorageDirectLoadOverride(socketInputFlows, writerFactory, catalog, config, client, pathFactory)
