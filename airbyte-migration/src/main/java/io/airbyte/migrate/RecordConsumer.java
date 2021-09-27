/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;

public class RecordConsumer implements CloseableConsumer<JsonNode> {

  private final CloseableConsumer<JsonNode> consumer;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JsonNode schema;

  public RecordConsumer(BufferedWriter fileWriter, JsonSchemaValidator jsonSchemaValidator, JsonNode schema) {
    this.consumer = Yamls.listWriter(fileWriter);
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.schema = schema;
  }

  @Override
  public void accept(JsonNode jsonNode) {
    try {
      jsonSchemaValidator.ensure(schema, jsonNode);
      consumer.accept(jsonNode);
    } catch (JsonValidationException e) {
      throw new IllegalArgumentException("Output record does not conform to declared output schema", e);
    }
  }

  @Override
  public void close() throws Exception {
    consumer.close();
  }

}
