/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DEFAULT_COMPRESSION_TYPE;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.CompressionTypeHelper;
import java.util.Objects;

public class S3JsonlFormatConfig implements S3FormatConfig {

  public static final String JSONL_SUFFIX = ".jsonl";

  private final Long partSize;
  private final CompressionType compressionType;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this.partSize = formatConfig.has(PART_SIZE_MB_ARG_NAME)
        ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong()
        : S3DestinationConstants.DEFAULT_PART_SIZE_MB;
    this.compressionType = formatConfig.has(COMPRESSION_ARG_NAME)
        ? CompressionTypeHelper.parseCompressionType(formatConfig.get(COMPRESSION_ARG_NAME))
        : DEFAULT_COMPRESSION_TYPE;
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
    return JSONL_SUFFIX + compressionType.getFileExtension();
  }

  public CompressionType getCompressionType() {
    return compressionType;
  }

  @Override
  public String toString() {
    return "S3JsonlFormatConfig{" +
        ", partSize=" + partSize +
        ", compression=" + compressionType.name() +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final S3JsonlFormatConfig that = (S3JsonlFormatConfig) o;
    return Objects.equals(partSize, that.partSize) && Objects.equals(compressionType, that.compressionType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(partSize, compressionType);
  }

}
