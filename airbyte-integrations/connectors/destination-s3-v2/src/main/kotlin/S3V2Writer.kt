/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.object_storage.ObjectStorageStreamLoaderFactory
import jakarta.inject.Singleton

@Singleton
class S3V2Writer(
    private val streamLoaderFactory: ObjectStorageStreamLoaderFactory<S3Object, *>,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.create(stream)
    }
}
