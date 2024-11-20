/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import javax.inject.Singleton

@Singleton
class IcebergV2Writer : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // TODO instantiate an actual IcebergStreamLoader
        return object : StreamLoader {
            override val stream = stream

            override suspend fun processRecords(
                records: Iterator<DestinationRecord>,
                totalSizeBytes: Long
            ) = SimpleBatch(state = Batch.State.COMPLETE)

            override suspend fun processFile(file: DestinationFile): Batch {
                throw NotImplementedError()
            }
        }
    }
}
