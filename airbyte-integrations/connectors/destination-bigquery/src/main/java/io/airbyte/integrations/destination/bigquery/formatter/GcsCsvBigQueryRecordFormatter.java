/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;

/**
 * Formatter for GCS CSV uploader. Contains specific filling of default Airbyte attributes. Note!
 * That it might be extended during CSV GCS integration.
 */
public class GcsCsvBigQueryRecordFormatter extends DefaultBigQueryRecordFormatter {

  public GcsCsvBigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

}
