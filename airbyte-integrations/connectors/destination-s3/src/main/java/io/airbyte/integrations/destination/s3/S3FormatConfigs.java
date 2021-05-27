package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;

public class S3FormatConfigs {

  public static S3FormatConfig getS3FormatConfig(JsonNode config) {
    JsonNode formatConfig = config.get("format");
    S3Format formatType = S3Format.valueOf(formatConfig.get("format_type").asText());

    if (formatType == S3Format.CSV) {
      Flattening flattening = Flattening.fromValue(formatConfig.get("csv_flattening").asText());
      return new S3CsvFormatConfig(flattening);
    }

    throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
  }

}
