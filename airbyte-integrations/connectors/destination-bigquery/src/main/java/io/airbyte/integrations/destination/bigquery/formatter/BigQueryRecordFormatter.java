/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage;
import io.airbyte.commons.json.Jsons;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
public class BigQueryRecordFormatter {

  public static final Schema SCHEMA_V2 = Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_META, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64));

  public BigQueryRecordFormatter() {}

  public String formatRecord(PartialAirbyteMessage recordMessage, long generationId) {
    final ObjectNode record = (ObjectNode) Jsons.emptyObject();
    record.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, UUID.randomUUID().toString());
    record.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, getEmittedAtField(recordMessage.getRecord()));
    record.set(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, NullNode.instance);
    record.put(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getSerialized());
    record.put(JavaBaseConstants.COLUMN_NAME_AB_META, Jsons.serialize(recordMessage.getRecord().getMeta()));
    record.put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId);
    return Jsons.serialize(record);
  }

  private String getEmittedAtField(final PartialAirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    return QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
  }

}
