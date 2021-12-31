/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class GcsBigQueryDenormalizedRecordFormatter extends DefaultBigQueryDenormalizedRecordFormatter {

  public GcsBigQueryDenormalizedRecordFormatter(
                                                final JsonNode jsonSchema,
                                                final StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  protected JsonNode formatJsonSchema(final JsonNode jsonSchema) {
    var textJson = Jsons.serialize(jsonSchema);
    // Add string type for Refs
    // Avro header convertor requires types for all fields
    textJson = textJson.replace("{\"$ref\":\"", "{\"type\":[\"string\"], \"$ref\":\"");
    return super.formatJsonSchema(Jsons.deserialize(textJson));
  }

  @Override
  protected void addAirbyteColumns(final ObjectNode data, final AirbyteRecordMessage recordMessage) {
    final long emittedAtMicroseconds = TimeUnit.MILLISECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);

    data.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    data.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, emittedAtMicroseconds);
  }

}
