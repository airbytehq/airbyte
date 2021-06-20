package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public class S3AvroFormatConfig implements S3FormatConfig {

  public S3AvroFormatConfig(JsonNode formatConfig) {
  }

  @Override
  public S3Format getFormat() {
    return S3Format.AVRO;
  }

}
