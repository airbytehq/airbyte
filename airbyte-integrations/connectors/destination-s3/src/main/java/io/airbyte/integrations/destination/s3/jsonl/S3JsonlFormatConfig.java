/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public class S3JsonlFormatConfig implements S3FormatConfig {

  private final Long partSize;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this.partSize = formatConfig.get(PART_SIZE_MB_ARG_NAME) != null
        ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong()
        : S3DestinationConstants.DEFAULT_PART_SIZE_MB;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.JSONL;
  }

  public Long getPartSize() {
    return partSize;
  }

}
