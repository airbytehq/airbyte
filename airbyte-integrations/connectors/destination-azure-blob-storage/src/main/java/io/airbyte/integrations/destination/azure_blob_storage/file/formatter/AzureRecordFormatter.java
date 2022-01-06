/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
public abstract class AzureRecordFormatter {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureRecordFormatter.class);

  private final Map<String, Set<String>> mapOfFailedFields = new HashMap<>();
  protected final StandardNameTransformer namingResolver;
  protected final JsonNode jsonSchema;

  public AzureRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
    this.namingResolver = namingResolver;
    this.jsonSchema = formatJsonSchema(jsonSchema.deepCopy());
  }

  protected JsonNode formatJsonSchema(JsonNode jsonSchema) {
    // Do nothing by default
    return jsonSchema;
  };

  public abstract JsonNode formatRecord(AirbyteRecordMessage recordMessage);

  public JsonNode getJsonSchema() {
    return jsonSchema;
  }

  protected void logFieldFail(String error, String fieldName) {
    mapOfFailedFields.putIfAbsent(error, new HashSet<>());
    mapOfFailedFields.get(error).add(fieldName);
  }

  public void printAndCleanFieldFails() {
    if (!mapOfFailedFields.isEmpty()) {
      mapOfFailedFields.forEach(
          (error, fieldNames) -> LOGGER.warn(
              "Field(s) fail with error {}. Fields : {} ",
              error,
              String.join(", ", fieldNames)));
      mapOfFailedFields.clear();
    } else {
      LOGGER.info("No field fails during record format.");
    }
  }

}
