/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3FormatConfigs {

  protected static final Logger LOGGER = LoggerFactory.getLogger(S3FormatConfigs.class);

  public static S3FormatConfig getS3FormatConfig(final JsonNode config) {
    final JsonNode formatConfig = config.get("format");
    LOGGER.info("S3 format config: {}", formatConfig.toString());
    final S3Format formatType = S3Format.valueOf(formatConfig.get("format_type").asText().toUpperCase());

    switch (formatType) {
      case AVRO -> {
        return new S3AvroFormatConfig(formatConfig);
      }
      case CSV -> {
        return new S3CsvFormatConfig(formatConfig);
      }
      case JSONL -> {
        return new S3JsonlFormatConfig(formatConfig);
      }
      case PARQUET -> {
        return new S3ParquetFormatConfig(formatConfig);
      }
      default -> {
        throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
      }
    }
  }

}
