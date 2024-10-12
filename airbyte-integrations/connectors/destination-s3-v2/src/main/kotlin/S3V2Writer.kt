/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

@Singleton
class S3V2Writer : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return S3V2StreamLoader(stream)
    }

    inner class S3V2StreamLoader(override val stream: DestinationStream) : StreamLoader {
        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long
        ): Batch = SimpleBatch(state = Batch.State.COMPLETE)
    }
}
