/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_onelake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoaderFactory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * Microsoft OneLake destination writer.
 *
 * Delegates stream loading to the CDK's [ObjectStorageStreamLoaderFactory], which handles
 * chunking, compression, and upload orchestration. The OneLake-specific configuration
 * (endpoint, path prefix, auth) is injected via [MicrosoftOneLakeConfiguration].
 */
@Singleton
@Primary
class MicrosoftOneLakeWriter(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<AzureBlob, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}

