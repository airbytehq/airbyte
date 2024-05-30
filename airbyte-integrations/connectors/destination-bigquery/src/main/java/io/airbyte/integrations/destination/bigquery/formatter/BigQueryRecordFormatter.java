/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage;
import io.airbyte.commons.json.Jsons;
import java.util.HashMap;
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
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));

  public BigQueryRecordFormatter() {}

  public String formatRecord(PartialAirbyteMessage recordMessage) {
    // Map.of has a @NonNull requirement, so creating a new Hash map
    final HashMap<String, Object> destinationV2record = new HashMap<>();
    destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, UUID.randomUUID().toString());
    destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, getEmittedAtField(recordMessage.getRecord()));
    destinationV2record.put(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, null);
    destinationV2record.put(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getSerialized());
    return Jsons.serialize(destinationV2record);
  }

  private Object getEmittedAtField(final PartialAirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    return QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
  }

}
