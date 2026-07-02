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

/**
 * Mirror of S3V2Writer. The only difference is that the generic [ObjectStorageStreamLoaderFactory]
 * is parameterized on [GcsBlob] instead of S3Object. Everything else (truncate/overwrite cleanup +
 * destination-state persistence) is generic CDK code, so the OVERWRITE prefix-purge behavior
 * matches v0.4.x semantically (the ObjectStorageStreamLoader deletes prior objects under the stream
 * prefix on truncate).
 */
@Singleton
class GcsV2Writer(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<GcsBlob, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}
