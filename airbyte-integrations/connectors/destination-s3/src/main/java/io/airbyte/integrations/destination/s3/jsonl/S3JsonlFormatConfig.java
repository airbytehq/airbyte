/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public class S3JsonlFormatConfig implements S3FormatConfig {

  public static final String JSONL_GZ_SUFFIX = ".jsonl.gz";
  public static final String JSONL_SUFFIX = ".jsonl";

  private final Long partSize;
  private final boolean gzipCompression;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this.partSize = formatConfig.has(PART_SIZE_MB_ARG_NAME)
        ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong()
        : S3DestinationConstants.DEFAULT_PART_SIZE_MB;
    this.gzipCompression = formatConfig.has(COMPRESSION_ARG_NAME)
        ? formatConfig.get(COMPRESSION_ARG_NAME).asBoolean()
        : S3DestinationConstants.DEFAULT_GZIP_COMPRESSION;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.JSONL;
  }

  public Long getPartSize() {
    return partSize;
  }

  @Override
  public String getFileExtension() {
    return gzipCompression ? JSONL_GZ_SUFFIX : JSONL_SUFFIX;
  }

  public boolean isGzipCompression() {
    return gzipCompression;
  }

}
