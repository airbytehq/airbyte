/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.StandardNameTransformer;

/**
 * Formatter for GCS CSV uploader. Contains specific filling of default Airbyte attributes. Note!
 * That it might be extended during CSV GCS integration.
 */
public class GcsCsvBigQueryRecordFormatter extends DefaultBigQueryRecordFormatter {

  public static final com.google.cloud.bigquery.Schema CSV_SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));

  public GcsCsvBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public Schema getBigQuerySchema(JsonNode jsonSchema) {
    if (TypingAndDedupingFlag.isDestinationV2()) {
      // not sure if this needs overridden :|
      return SCHEMA_V2;
    } else {
      return CSV_SCHEMA;
    }
  }

}
