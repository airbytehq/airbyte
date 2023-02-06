/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

/**
 * Formatter for GCS Avro uploader. Contains specific filling of default Airbyte attributes.
 */
public class GcsAvroBigQueryRecordFormatter extends DefaultBigQueryRecordFormatter {

  public GcsAvroBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  protected Object getEmittedAtField(AirbyteRecordMessage recordMessage) {
    return recordMessage.getEmittedAt();
  }

  @Override
  protected Object getData(AirbyteRecordMessage recordMessage) {
    return StandardNameTransformer.formatJsonPath(recordMessage.getData()).toString();
  }

}
