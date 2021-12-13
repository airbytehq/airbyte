/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public record S3JsonlFormatConfig(Long partSize) implements S3FormatConfig {

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this(formatConfig.get(PART_SIZE_MB_ARG_NAME) != null ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong() : null);
  }

  @Override
  public S3Format format() {
    return S3Format.JSONL;
  }
}
