package io.dataline.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.*;
import io.dataline.config.SourceConnectionSpecification;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class SourceConnectionImplementationValidation {
  private final ConfigPersistence configPersistence;

  public SourceConnectionImplementationValidation(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public void validate(UUID sourceSpecificationId, Object object) {
    final SourceConnectionSpecification sourceConnectionSpecification =
        configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
            sourceSpecificationId.toString(),
            SourceConnectionSpecification.class);

    final Object schema = sourceConnectionSpecification.getSpecification();
  }

  // todo: a lot of this is copied from ConfigPersistenceImpl
  private void validateJson(UUID sourceConnectionSpecificationId, Object configuration) {
    final SourceConnectionSpecification sourceConnectionSpecification =
        configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
            sourceConnectionSpecificationId.toString(),
            SourceConnectionSpecification.class);

    final ObjectMapper objectMapper = new ObjectMapper();
    final SchemaValidatorsConfig schemaValidatorsConfig = new SchemaValidatorsConfig();
    final JsonSchemaFactory jsonSchemaFactory =
        JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);

    final JsonNode schemaJson =
        objectMapper.valueToTree(sourceConnectionSpecification.getSpecification());
    final JsonNode configJson = objectMapper.valueToTree(configuration);
    JsonSchema schema = jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig);

    Set<ValidationMessage> validationMessages = schema.validate(configJson);
    if (validationMessages.size() > 0) {
      throw new IllegalStateException(
          String.format(
              "json schema validation failed. type: %s id: %s \n errors: %s \n schema: \n%s \n object: \n%s",
              PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
              sourceConnectionSpecificationId,
              validationMessages.stream()
                  .map(ValidationMessage::toString)
                  .collect(Collectors.joining(",")),
              schema.getSchemaNode().toPrettyString(),
              configJson.toPrettyString()));
    }
  }
}
