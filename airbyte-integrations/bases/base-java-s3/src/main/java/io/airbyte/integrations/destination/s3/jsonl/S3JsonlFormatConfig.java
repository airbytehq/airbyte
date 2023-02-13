/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.CompressionTypeHelper;
import io.airbyte.integrations.destination.s3.util.FlatteningType;
import io.airbyte.integrations.destination.s3.util.FlatteningTypeHelper;
import java.util.Objects;

public class S3JsonlFormatConfig implements S3FormatConfig {

  public static final String JSONL_SUFFIX = ".jsonl";

  private final FlatteningType flatteningType;

  private final CompressionType compressionType;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this(
        formatConfig.has(FLATTENING_TYPE_ARG_NAME)
            ? FlatteningTypeHelper.fromValue(formatConfig.get(FLATTENING_TYPE_ARG_NAME).asText())
            : DEFAULT_FLATTENING_TYPE,
        formatConfig.has(COMPRESSION_ARG_NAME)
            ? CompressionTypeHelper.parseCompressionType(formatConfig.get(COMPRESSION_ARG_NAME))
            : DEFAULT_COMPRESSION_TYPE);
  }

  public S3JsonlFormatConfig(final FlatteningType flatteningType, final CompressionType compressionType) {
    this.flatteningType = flatteningType;
    this.compressionType = compressionType;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.JSONL;
  }

  @Override
  public String getFileExtension() {
    return JSONL_SUFFIX + compressionType.getFileExtension();
  }

  public CompressionType getCompressionType() {
    return compressionType;
  }

  public FlatteningType getFlatteningType() {
    return flatteningType;
  }

  @Override
  public String toString() {
    return "S3JsonlFormatConfig{" +
        "compressionType=" + compressionType +
        ", flattening=" + flatteningType +
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
    return flatteningType == that.flatteningType
        && Objects.equals(compressionType, that.compressionType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(flatteningType, compressionType);
  }

}
