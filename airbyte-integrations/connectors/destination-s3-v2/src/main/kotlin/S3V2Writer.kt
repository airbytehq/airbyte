/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.DestinationRecordToAirbyteValueWithMeta
import io.airbyte.cdk.load.data.toJson
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

private val logger = KotlinLogging.logger {}

@Singleton
class S3V2Writer(
    private val s3Client: S3Client,
    private val pathFactory: ObjectStoragePathFactory,
    private val recordDecorator: DestinationRecordToAirbyteValueWithMeta,
) : DestinationWriter {
    sealed interface S3V2Batch : Batch
    data class StagedObject(
        override val state: Batch.State = Batch.State.PERSISTED,
        val s3Object: S3Object,
        val partNumber: Long
    ) : S3V2Batch
    data class FinalizedObject(
        override val state: Batch.State = Batch.State.COMPLETE,
        val s3Object: S3Object,
    ) : S3V2Batch

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return S3V2StreamLoader(stream)
    }

    @SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
    inner class S3V2StreamLoader(override val stream: DestinationStream) : StreamLoader {
        private val partNumber = AtomicLong(0L) // TODO: Get from destination state

        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long
        ): Batch {
            val partNumber = partNumber.getAndIncrement()
            val key = pathFactory.getPathToFile(stream, partNumber, isStaging = true).toString()
            logger.info { "EDGAO DEBUG starting upload" }
            val s3Object =
                s3Client.streamingUpload(key) { writer ->
                    records.forEach {
                        val serialized = recordDecorator.decorate(it).toJson().serializeToString()
                        writer.write(serialized)
                        writer.write("\n")
                    }
                }
            logger.info { "EDGAO DEBUG finished upload, returning staged object batch" }
            return StagedObject(s3Object = s3Object, partNumber = partNumber)
        }

        override suspend fun processBatch(batch: Batch): Batch {
            val stagedObject = batch as StagedObject
            val finalKey =
                pathFactory
                    .getPathToFile(stream, stagedObject.partNumber, isStaging = false)
                    .toString()
            logger.info { "EDGAO DEBUG moving file" }
            val newObject = s3Client.move(stagedObject.s3Object, finalKey)
            logger.info { "EDGAO DEBUG moved file, returning finalized object batch" }
            val finalizedObject = FinalizedObject(s3Object = newObject)
            return finalizedObject
        }
    }
}
