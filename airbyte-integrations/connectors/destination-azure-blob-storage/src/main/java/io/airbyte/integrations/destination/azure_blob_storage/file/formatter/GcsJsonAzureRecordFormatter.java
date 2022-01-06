/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;

/**
 * Formatter for GCS CSV uploader. Contains specific filling of default Airbyte attributes. Note!
 * That it might be extended during CSV GCS integration.
 */
public class GcsJsonAzureRecordFormatter extends DefaultAzureRecordFormatter {

  public GcsJsonAzureRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

}
