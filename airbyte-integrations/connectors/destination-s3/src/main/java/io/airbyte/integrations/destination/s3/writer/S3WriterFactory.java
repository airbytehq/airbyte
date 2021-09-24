/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;

/**
 * Create different {@link S3Writer} based on {@link S3DestinationConfig}.
 */
public interface S3WriterFactory {

  S3Writer create(S3DestinationConfig config,
                  AmazonS3 s3Client,
                  ConfiguredAirbyteStream configuredStream,
                  Timestamp uploadTimestamp)
      throws Exception;

}
