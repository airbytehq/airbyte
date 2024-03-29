/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.sql.Timestamp

/** Create different [DestinationFileWriter] based on [S3DestinationConfig]. */
interface S3WriterFactory {
    @Throws(Exception::class)
    fun create(
        config: S3DestinationConfig,
        s3Client: AmazonS3,
        configuredStream: ConfiguredAirbyteStream,
        uploadTimestamp: Timestamp
    ): DestinationFileWriter?
}
