/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;

public record S3CsvFormatConfig(Flattening flattening, Long partSize) implements S3FormatConfig {

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

  public S3CsvFormatConfig(final JsonNode formatConfig) {
    this(
        Flattening.fromValue(formatConfig.get("flattening").asText()),
        formatConfig.get(PART_SIZE_MB_ARG_NAME) != null ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong() : null
    );
  }

  @Override
  public S3Format format() {
    return S3Format.CSV;
  }
}
