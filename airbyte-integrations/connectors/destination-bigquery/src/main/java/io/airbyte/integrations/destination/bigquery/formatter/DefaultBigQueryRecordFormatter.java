/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * Default BigQuery formatter. Represents default Airbyte schema (three columns). Note! Default
 * formatter is used inside Direct uploader.
 */
public class DefaultBigQueryRecordFormatter extends BigQueryRecordFormatter {

  public static final com.google.cloud.bigquery.Schema SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));

  public static final com.google.cloud.bigquery.Schema SCHEMA_V2 = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.JSON));

  public DefaultBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public JsonNode formatRecord(AirbyteRecordMessage recordMessage) {
    if (TypingAndDedupingFlag.isDestinationV2()) {
      // Map.of has a @NonNull requirement, so creating a new Hash map
      final HashMap<String, Object> destinationV2record = new HashMap<>();
      destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, UUID.randomUUID().toString());
      destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, getEmittedAtField(recordMessage));
      destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, null);
      if (useObjectForData()) {
        destinationV2record.put(JavaBaseConstants.COLUMN_NAME_DATA,
            StandardNameTransformer.formatJsonPath(recordMessage.getData()));
      } else {
        destinationV2record.put(JavaBaseConstants.COLUMN_NAME_DATA, getData(recordMessage));
      }
      return Jsons.jsonNode(destinationV2record);
    } else {
      return Jsons.jsonNode(Map.of(
          JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT, getEmittedAtField(recordMessage),
          JavaBaseConstants.COLUMN_NAME_DATA, getData(recordMessage)));
    }
  }

  protected Object getEmittedAtField(AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    return QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
  }

  protected Object getData(AirbyteRecordMessage recordMessage) {
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.serialize(formattedData);
  }

  @Override
  public Schema getBigQuerySchema(JsonNode jsonSchema) {
    if (TypingAndDedupingFlag.isDestinationV2()) {
      return SCHEMA_V2;
    } else {
      return SCHEMA;
    }
  }

}
