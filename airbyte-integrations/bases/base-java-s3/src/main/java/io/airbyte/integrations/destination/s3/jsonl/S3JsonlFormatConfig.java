/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DEFAULT_COMPRESSION_TYPE;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.FLATTENING_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.CompressionTypeHelper;
import io.airbyte.integrations.destination.s3.util.Flattening;
import java.util.Objects;
import lombok.ToString;

@ToString
public class S3JsonlFormatConfig implements S3FormatConfig {

  public static final String JSONL_SUFFIX = ".jsonl";

  private final Flattening flattening;

  private final CompressionType compressionType;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this(
        formatConfig.has(FLATTENING_ARG_NAME)
            ? Flattening.fromValue(formatConfig.get(FLATTENING_ARG_NAME).asText())
            : Flattening.NO,
        formatConfig.has(COMPRESSION_ARG_NAME)
            ? CompressionTypeHelper.parseCompressionType(formatConfig.get(COMPRESSION_ARG_NAME))
            : DEFAULT_COMPRESSION_TYPE);
  }

  public S3JsonlFormatConfig(final Flattening flattening, final CompressionType compressionType) {
    this.flattening = flattening;
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

  public Flattening getFlatteningType() {
    return flattening;
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
    return flattening == that.flattening
        && Objects.equals(compressionType, that.compressionType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(flattening, compressionType);
  }

}
