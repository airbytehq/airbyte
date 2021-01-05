package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.closeable.CloseableConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.IOException;

public class RecordConsumer implements CloseableConsumer<JsonNode> {

  private final BufferedWriter fileWriter;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JsonNode schema;

  public RecordConsumer(BufferedWriter fileWriter, JsonSchemaValidator jsonSchemaValidator, JsonNode schema) {

    this.fileWriter = fileWriter;
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.schema = schema;
  }

  @Override
  public void accept(JsonNode jsonNode) {
    // todo validate.
    try {
      jsonSchemaValidator.ensure(jsonNode, schema);
      fileWriter.write(Jsons.serialize(jsonNode));
      fileWriter.newLine();
    } catch (IOException | JsonValidationException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    fileWriter.close();
  }

}
