/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoaderFactory
import jakarta.inject.Singleton

/** Destination writer that delegates to the CDK's [ObjectStorageStreamLoaderFactory] for GCS. */
@Singleton
class GcsV2Writer(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<GcsBlob, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}
