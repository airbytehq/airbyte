/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.protocol.models.AirbyteRecordMessage;

public class TestBigQueryDenormalizedRecordFormatter extends
    DefaultBigQueryDenormalizedRecordFormatter {

  public TestBigQueryDenormalizedRecordFormatter(
                                                 JsonNode jsonSchema,
                                                 StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public void addAirbyteColumns(ObjectNode data,
                                AirbyteRecordMessage recordMessage) {
    // this method just exposes a protected method for testing making it public
    super.addAirbyteColumns(data, recordMessage);
  }

}
