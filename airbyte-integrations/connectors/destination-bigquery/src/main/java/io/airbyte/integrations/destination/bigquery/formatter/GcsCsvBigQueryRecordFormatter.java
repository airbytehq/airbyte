/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;

public class GcsCsvBigQueryRecordFormatter extends DefaultBigQueryRecordFormatter {

  public GcsCsvBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

}
