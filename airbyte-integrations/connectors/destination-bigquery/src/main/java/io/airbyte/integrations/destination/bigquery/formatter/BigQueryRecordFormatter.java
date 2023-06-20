/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Schema;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
public abstract class BigQueryRecordFormatter {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordFormatter.class);

  protected Schema bigQuerySchema;
  protected final Map<String, Set<String>> mapOfFailedFields = new HashMap<>();
  protected final StandardNameTransformer namingResolver;
  protected final JsonNode originalJsonSchema;
  protected JsonNode jsonSchema;

  /**
   * These parameters are required for the correct operation of denormalize version of the connector.
   */
  protected final Set<String> invalidKeys = new HashSet<>();
  protected final Set<String> fieldsContainRefDefinitionValue = new HashSet<>();

  public BigQueryRecordFormatter(final JsonNode jsonSchema, final StandardNameTransformer namingResolver) {
    this.namingResolver = namingResolver;
    this.originalJsonSchema = jsonSchema.deepCopy();
    this.jsonSchema = formatJsonSchema(jsonSchema.deepCopy());
  }

  protected JsonNode formatJsonSchema(final JsonNode jsonSchema) {
    // Do nothing by default
    return jsonSchema;
  };

  /***
   * To write to a JSON type, Standard inserts needs the Json to be an object. For Avro however, it
   * needs to be a string. The column in the schema remains JSON regardless.
   *
   * @return whether to use an object for the formatting of the record.
   */
  protected boolean useObjectForData() {
    return true;
  }

  public abstract JsonNode formatRecord(AirbyteRecordMessage recordMessage);

  public Schema getBigQuerySchema() {
    if (bigQuerySchema == null) {
      bigQuerySchema = getBigQuerySchema(jsonSchema);
    }
    return bigQuerySchema;
  }

  public JsonNode getJsonSchema() {
    return jsonSchema;
  }

  protected abstract Schema getBigQuerySchema(JsonNode jsonSchema);

  protected void logFieldFail(final String error, final String fieldName) {
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
    }
  }

}
