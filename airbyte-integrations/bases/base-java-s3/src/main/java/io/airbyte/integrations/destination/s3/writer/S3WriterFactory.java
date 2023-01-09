/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;

/**
 * Create different {@link DestinationFileWriter} based on {@link S3DestinationConfig}.
 */
public interface S3WriterFactory {

  DestinationFileWriter create(S3DestinationConfig config,
                               AmazonS3 s3Client,
                               ConfiguredAirbyteStream configuredStream,
                               Timestamp uploadTimestamp)
      throws Exception;

}
