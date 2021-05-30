package io.airbyte.integrations.destination.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;

/**
 * Create different {@link S3OutputFormatter} based on {@link S3DestinationConfig}.
 */
public interface S3OutputFormatterFactory {

  S3OutputFormatter create(S3DestinationConfig config,
                           AmazonS3 s3Client,
                           ConfiguredAirbyteStream configuredStream,
                           Timestamp uploadTimestamp) throws IOException;

}
