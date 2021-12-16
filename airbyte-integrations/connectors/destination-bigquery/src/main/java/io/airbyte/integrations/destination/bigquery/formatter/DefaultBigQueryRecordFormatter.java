/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class DefaultBigQueryRecordFormatter extends BigQueryRecordFormatter {

  private static final com.google.cloud.bigquery.Schema SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));

  public DefaultBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public JsonNode formatRecord(AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
  }

  @Override
  public Schema getBigQuerySchema(JsonNode jsonSchema) {
    return SCHEMA;
  }

}
