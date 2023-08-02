/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DEFAULT_COMPRESSION_TYPE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.CompressionTypeHelper;
import io.airbyte.integrations.destination.s3.util.Flattening;
import java.util.Objects;

public class S3CsvFormatConfig implements S3FormatConfig {

  public static final String CSV_SUFFIX = ".csv";

  private final Flattening flattening;
  private final CompressionType compressionType;

  public S3CsvFormatConfig(final JsonNode formatConfig) {
    this(
        Flattening.fromValue(formatConfig.has("flattening") ? formatConfig.get("flattening").asText() : Flattening.NO.getValue()),
        formatConfig.has(COMPRESSION_ARG_NAME)
            ? CompressionTypeHelper.parseCompressionType(formatConfig.get(COMPRESSION_ARG_NAME))
            : DEFAULT_COMPRESSION_TYPE);
  }

  public S3CsvFormatConfig(final Flattening flattening, final CompressionType compressionType) {
    this.flattening = flattening;
    this.compressionType = compressionType;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.CSV;
  }

  public Flattening getFlattening() {
    return flattening;
  }

  @Override
  public String getFileExtension() {
    return CSV_SUFFIX + compressionType.getFileExtension();
  }

  public CompressionType getCompressionType() {
    return compressionType;
  }

  @Override
  public String toString() {
    return "S3CsvFormatConfig{" +
        "flattening=" + flattening +
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
    final S3CsvFormatConfig that = (S3CsvFormatConfig) o;
    return flattening == that.flattening
        && Objects.equals(compressionType, that.compressionType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(flattening, compressionType);
  }

}
