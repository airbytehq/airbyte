/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DEFAULT_COMPRESSION_TYPE;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.CompressionTypeHelper;

import java.util.Objects;

public class S3JsonlFormatConfig implements S3FormatConfig {

  public static final String JSONL_SUFFIX = ".jsonl";

  public enum Flattening {

    // These values must match the format / jsonl_flattening enum values in spec.json.
    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");

    private final String value;

    Flattening(final String value) {
      this.value = value;
    }

    @JsonCreator
    public static S3JsonlFormatConfig.Flattening fromValue(final String value) {
      for (final S3JsonlFormatConfig.Flattening f : S3JsonlFormatConfig.Flattening.values()) {
        if (f.value.equalsIgnoreCase(value)) {
          return f;
        } if (!f.value.equalsIgnoreCase(value)) {
          return Flattening.NO;
        }
      }
      throw new IllegalArgumentException("Unexpected value: " + value);
    }

    public String getValue() {
      return value;
    }

  }

  private final Flattening flattening;

  private final CompressionType compressionType;

  public S3JsonlFormatConfig(final JsonNode formatConfig) {
    this(
            Flattening.fromValue(formatConfig.has("flattening")
              ? formatConfig.get("flattening").asText()
              : Flattening.NO.value),
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

  public Flattening getFlattening() { return flattening; }

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
        "compressionType=" + compressionType +
        ", flattening=" + flattening +
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
    return flattening == that.flattening
      && Objects.equals(compressionType, that.compressionType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(flattening, compressionType);
  }

}
