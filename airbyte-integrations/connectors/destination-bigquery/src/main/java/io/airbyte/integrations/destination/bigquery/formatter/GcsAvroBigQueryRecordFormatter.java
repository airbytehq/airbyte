/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class GcsAvroBigQueryRecordFormatter extends DefaultBigQueryRecordFormatter {

  public GcsAvroBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public JsonNode formatRecord(AirbyteRecordMessage recordMessage) {
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, formattedData.toString(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, emittedAtMicroseconds));
  }

}
