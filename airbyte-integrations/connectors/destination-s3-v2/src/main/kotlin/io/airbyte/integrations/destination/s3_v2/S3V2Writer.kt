/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.createS3Client
import io.airbyte.cdk.load.command.toPathFactory
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.spark.S3Object
import io.airbyte.cdk.load.spark.SparkS3WriterFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

@Singleton
class S3V2Writer(
    val config: S3V2Configuration,
    timeProvider: TimeProvider,
    sparkS3WriterFactory: SparkS3WriterFactory,
) : DestinationWriter {
    val s3Client = config.createS3Client()
    val s3Writer = sparkS3WriterFactory.create(s3Client)
    val pathFactory = config.toPathFactory(timeProvider.now())

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return S3V2StreamLoader(stream)
    }

    inner class S3V2StreamLoader(
        override val stream: DestinationStream,
    ) : StreamLoader {
        private val filePart = AtomicLong(0L)
        private val stagingDirectory = pathFactory.getDirectory(stream, isStaging = true)

        override suspend fun processStagedLocalFile(localFile: SpilledRawMessagesLocalFile): Batch {
            return s3Writer.write(stream.schema, localFile, stagingDirectory, config.outputFormat)
        }

        override suspend fun processBatch(batch: Batch): Batch {
            batch as S3Object
            val newPath = pathFactory.getFinalFilePath(stream, filePart.getAndIncrement())
            val moved = s3Client.move(batch, newPath)
            return moved.copy(state = Batch.State.COMPLETE)
        }
    }
}
