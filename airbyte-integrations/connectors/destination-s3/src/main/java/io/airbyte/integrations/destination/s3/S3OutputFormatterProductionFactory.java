package io.airbyte.integrations.destination.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.csv.S3CsvOutputFormatter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;

public class S3OutputFormatterProductionFactory implements S3OutputFormatterFactory {

  @Override
  public S3OutputFormatter create(S3DestinationConfig config, AmazonS3 s3Client,
      ConfiguredAirbyteStream configuredStream, Timestamp uploadTimestamp) throws IOException {
    S3Format format = config.getFormatConfig().getFormat();
    if (format == S3Format.CSV) {
      return new S3CsvOutputFormatter(config, s3Client, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected S3 destination format: " + format);
  }

}
