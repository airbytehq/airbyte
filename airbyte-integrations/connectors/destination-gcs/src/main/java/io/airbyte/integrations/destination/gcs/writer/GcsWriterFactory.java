/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;

/**
 * Create different {@link GcsWriterFactory} based on {@link GcsDestinationConfig}.
 */
public interface GcsWriterFactory {

  DestinationFileWriter create(GcsDestinationConfig config,
                               AmazonS3 s3Client,
                               ConfiguredAirbyteStream configuredStream,
                               Timestamp uploadTimestamp)
      throws Exception;

}
