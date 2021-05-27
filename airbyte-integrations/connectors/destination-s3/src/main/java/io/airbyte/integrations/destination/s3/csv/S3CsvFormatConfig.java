package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.annotation.JsonCreator;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import java.util.Locale;

public class S3CsvFormatConfig implements S3FormatConfig {

  public enum Flattening {
    // These values must match the format / csv_flattening enum values in spec.json.
    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");

    private final String value;

    Flattening(String value) {
      this.value = value;
    }

    @JsonCreator
    public static Flattening fromValue(String value) {
      for (Flattening b : Flattening.values()) {
        if (b.value.toLowerCase(Locale.ROOT).equals(value.toLowerCase())) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value: " + value);
    }
  }

  private final Flattening flattening;

  public S3CsvFormatConfig(
      Flattening flattening) {
    this.flattening = flattening;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.CSV;
  }

  public Flattening getFlattening() {
    return flattening;
  }

}
