/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import java.util.Objects;

public class S3CsvFormatConfig implements S3FormatConfig {

  public enum Flattening {

    // These values must match the format / csv_flattening enum values in spec.json.
    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");

    private final String value;

    Flattening(final String value) {
      this.value = value;
    }

    @JsonCreator
    public static Flattening fromValue(final String value) {
      for (final Flattening f : Flattening.values()) {
        if (f.value.equalsIgnoreCase(value)) {
          return f;
        }
      }
      throw new IllegalArgumentException("Unexpected value: " + value);
    }

    public String getValue() {
      return value;
    }

  }

  private final Flattening flattening;
  private final Long partSize;

  public S3CsvFormatConfig(final JsonNode formatConfig) {
    this(
        Flattening.fromValue(formatConfig.has("flattening") ? formatConfig.get("flattening").asText() : Flattening.NO.value),
        formatConfig.get(PART_SIZE_MB_ARG_NAME) != null
            ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong()
            : S3DestinationConstants.DEFAULT_PART_SIZE_MB);
  }

  public S3CsvFormatConfig(final Flattening flattening, final Long partSize) {
    this.flattening = flattening;
    this.partSize = partSize;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.CSV;
  }

  public Flattening getFlattening() {
    return flattening;
  }

  @Override
  public Long getPartSize() {
    return partSize;
  }

  @Override
  public String toString() {
    return "S3CsvFormatConfig{" +
        "flattening=" + flattening +
        ", partSize=" + partSize +
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
    return flattening == that.flattening && Objects.equals(partSize, that.partSize);
  }

  @Override
  public int hashCode() {
    return Objects.hash(flattening, partSize);
  }

}
