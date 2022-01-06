/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.util.Map;
import java.util.UUID;

/**
 * Default BigQuery formatter. Represents default Airbyte schema (three columns). Note! Default
 * formatter is used inside Direct uploader.
 */
public class DefaultAzureRecordFormatter extends AzureRecordFormatter {

  public DefaultAzureRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  @Override
  public JsonNode formatRecord(AirbyteRecordMessage recordMessage) {
    return Jsons.jsonNode(Map.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt(),
        JavaBaseConstants.COLUMN_NAME_DATA, getData(recordMessage)));
  }

  protected Object getData(AirbyteRecordMessage recordMessage) {
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.serialize(formattedData);
  }

}
