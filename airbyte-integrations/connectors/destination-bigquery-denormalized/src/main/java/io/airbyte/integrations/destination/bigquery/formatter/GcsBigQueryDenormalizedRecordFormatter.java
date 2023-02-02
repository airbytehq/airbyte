/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Schema;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
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
    return super.formatJsonSchema(FormatterUtil.replaceNoSchemaRef(jsonSchema));
  }

  @Override
  public Schema getBigQuerySchema(final JsonNode jsonSchema) {
    return super.getBigQuerySchema(FormatterUtil.replaceDateTime(jsonSchema));
  }

  @Override
  protected void addAirbyteColumns(final ObjectNode data, final AirbyteRecordMessage recordMessage) {
    final long emittedAtMicroseconds = TimeUnit.MILLISECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);

    data.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    data.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, emittedAtMicroseconds);
  }

}
