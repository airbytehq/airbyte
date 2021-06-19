package io.airbyte.integrations.destination.s3.jsonl;

import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public class S3JsonlFormatConfig implements S3FormatConfig {

  @Override
  public S3Format getFormat() {
    return S3Format.JSONL;
  }

}
