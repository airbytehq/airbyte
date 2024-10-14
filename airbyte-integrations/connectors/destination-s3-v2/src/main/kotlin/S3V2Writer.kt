/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.command.s3.S3Client
import io.airbyte.cdk.command.s3.S3Object
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValueToJson
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.util.concurrent.atomic.AtomicLong
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream

@Singleton
class S3V2Writer(
    config: S3V2Configuration,
    timeProvider: TimeProvider,
    val s3Client: S3Client,
) : DestinationWriter<S3Object> {
    val pathFactory = config.createPathFactory(timeProvider.currentTimeMillis())

    override fun createStreamLoader(stream: DestinationStream): StreamLoader<S3Object> {
        return S3V2StreamLoader(stream)
    }

    inner class S3V2StreamLoader(override val stream: DestinationStream) : StreamLoader<S3Object> {
        private val stagingPartNo = AtomicLong(0L) // TODO: Get from destination state
        private val finalPartNo = AtomicLong(0L) // TODO: Get from destination state

        override suspend fun start() {
            // TODO: Determine from destination state the list of files we need to delete at end of sync
        }

        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long
        ): Batch<S3Object> {
            val key = pathFactory.getPathWithFileName(stream, isStaging = true, partNumber = stagingPartNo.getAndIncrement())
            // TODO: Update destination state that we're about to write this object (for this gen id)
            val s3Object = s3Client.streamingUpload(key.toString()) {
                // TODO: (Maybe?) Alternately compose into parquet block (part size=0 => whatever i return here is the block?)
                if (records.hasNext()) {
                    val data = records.next().data
                    val json = AirbyteValueToJson().convert(data)
                    ObjectMapper().writeValueAsBytes(json)
                    // TODO: Newline!
                } else {
                    null
                }
            }.mapPart {
                // TODO: Conditionally compress based on destination config
                val buffer = ByteArrayOutputStream(it.size)
                GZIPOutputStream(buffer).write(it)
                buffer.toByteArray()
            }.upload()

            return Batch(Batch.State.PERSISTED, s3Object)
            // TODO: Update destination state that we've written this object (for this gen id)
        }

        override suspend fun processBatch(batch: Batch<S3Object>): Batch<S3Object> {
            // TODO: Update destination state that we're about to move this object (for this gen id)
            val newPath = pathFactory.getPathWithFileName(stream, isStaging = false, partNumber = finalPartNo.getAndIncrement())
            s3Client.move(batch.payload, newPath.toString())
            // TODO: Update destination state that we've moved this object (for this gen id)
            return batch.copy(state = Batch.State.COMPLETE)
        }

        override suspend fun close(streamFailure: StreamIncompleteResult?) {
            // TODO: Update destination state that we've finished writing all objects for this gen id
            // TODO: Delete the files we determined at start of sync
            // TODO: Update destination state that we've deleted these files
        }
    }
}
