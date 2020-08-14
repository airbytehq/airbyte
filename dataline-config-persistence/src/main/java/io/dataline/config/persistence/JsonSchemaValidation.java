package io.dataline.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SchemaValidatorsConfig;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import java.util.Set;
import java.util.stream.Collectors;

public class JsonSchemaValidation {
  private final SchemaValidatorsConfig schemaValidatorsConfig;
  private final JsonSchemaFactory jsonSchemaFactory;

  public JsonSchemaValidation() {
    this.schemaValidatorsConfig = new SchemaValidatorsConfig();
    this.jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
  }

  public Set<ValidationMessage> validate(JsonNode schemaJson, JsonNode configJson) {
    JsonSchema schema = jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig);

    return schema.validate(configJson);
  }

  public void validateThrow(JsonNode schemaJson, JsonNode configJson)
      throws JsonValidationException {
    final Set<ValidationMessage> validationMessages = validate(schemaJson, configJson);
    if (validationMessages.size() > 0) {
      throw new JsonValidationException(
          String.format(
              "json schema validation failed. \nerrors: %s \nschema: \n%s \nobject: \n%s",
              validationMessages.stream()
                  .map(ValidationMessage::toString)
                  .collect(Collectors.joining(",")),
              schemaJson.toPrettyString(),
              configJson.toPrettyString()));
    }
  }
}
