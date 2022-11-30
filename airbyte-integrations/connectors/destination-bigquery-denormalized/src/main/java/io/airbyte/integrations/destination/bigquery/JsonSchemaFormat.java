/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.StandardSQLTypeName;
import java.util.Arrays;
import java.util.List;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Mapping of JsonSchema formats to BigQuery Standard SQL types.
 */
public enum JsonSchemaFormat {

  DATE("date", null, StandardSQLTypeName.DATE),
  DATETIME("date-time", null, StandardSQLTypeName.DATETIME),
  DATETIME_WITH_TZ("date-time", "timestamp_with_timezone", StandardSQLTypeName.TIMESTAMP),
  TIME("time", null, StandardSQLTypeName.TIME),
  TIMESTAMP("timestamp-micros", null, StandardSQLTypeName.TIMESTAMP);

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonSchemaFormat.class);
  private final String jsonSchemaFormat;
  private final String jsonSchemaAirbyteType;
  private final StandardSQLTypeName bigQueryType;

  JsonSchemaFormat(final String jsonSchemaFormat, final String jsonSchemaAirbyteType, final StandardSQLTypeName bigQueryType) {
    this.jsonSchemaAirbyteType = jsonSchemaAirbyteType;
    this.jsonSchemaFormat = jsonSchemaFormat;
    this.bigQueryType = bigQueryType;
  }

  public static JsonSchemaFormat fromJsonSchemaFormat(final @Nonnull String jsonSchemaFormat, final @Nullable String jsonSchemaAirbyteType) {
    List<JsonSchemaFormat> matchFormats = null;
    // Match by Format + Type
    if (jsonSchemaAirbyteType != null) {
      matchFormats = Arrays.stream(values())
          .filter(format -> jsonSchemaFormat.equals(format.jsonSchemaFormat) && jsonSchemaAirbyteType.equals(format.jsonSchemaAirbyteType)).toList();
    }

    // Match by Format are no results already
    if (matchFormats == null || matchFormats.isEmpty()) {
      matchFormats =
          Arrays.stream(values()).filter(format -> jsonSchemaFormat.equals(format.jsonSchemaFormat) && format.jsonSchemaAirbyteType == null).toList();
    }

    if (matchFormats.isEmpty()) {
      return null;
    } else if (matchFormats.size() > 1) {
      throw new RuntimeException(
          "Match with more than one json format! Matched formats : " + matchFormats + ", Inputs jsonSchemaFormat : " + jsonSchemaFormat
              + ", jsonSchemaAirbyteType : " + jsonSchemaAirbyteType);
    } else {
      return matchFormats.get(0);
    }
  }

  public StandardSQLTypeName getBigQueryType() {
    return bigQueryType;
  }

  @Override
  public String toString() {
    return jsonSchemaFormat;
  }

}
