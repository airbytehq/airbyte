/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;

public class TestGcsBigQueryDenormalizedRecordFormatter extends
    GcsBigQueryDenormalizedRecordFormatter {

  public TestGcsBigQueryDenormalizedRecordFormatter(
                                                    JsonNode jsonSchema,
                                                    StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public JsonNode formatJsonSchema(JsonNode jsonSchema) {
    return super.formatJsonSchema(jsonSchema);
  }

}
