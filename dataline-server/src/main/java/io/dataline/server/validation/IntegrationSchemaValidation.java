package io.dataline.server.validation;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.persistence.*;
import java.util.UUID;

public class IntegrationSchemaValidation {
  private final ConfigPersistence configPersistence;

  private final ObjectMapper objectMapper;
  private final JsonSchemaValidation jsonSchemaValidation;

  public IntegrationSchemaValidation(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;

    this.objectMapper = new ObjectMapper();
    this.jsonSchemaValidation = new JsonSchemaValidation();
  }

  public void validateSourceConnectionConfiguration(
      UUID sourceConnectionSpecificationId, Object configuration)
      throws JsonValidationException, ConfigNotFoundException {
    final SourceConnectionSpecification sourceConnectionSpecification =
        configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
            sourceConnectionSpecificationId.toString(),
            SourceConnectionSpecification.class);

    final JsonNode schemaJson =
        objectMapper.valueToTree(sourceConnectionSpecification.getSpecification());
    final JsonNode configJson = objectMapper.valueToTree(configuration);

    jsonSchemaValidation.validateThrow(schemaJson, configJson);
  }

  public void validateDestinationConnectionConfiguration(
      UUID destinationConnectionSpecificationId, Object configuration)
      throws JsonValidationException, ConfigNotFoundException {
    final DestinationConnectionSpecification destinationConnectionSpecification =
        configPersistence.getConfig(
            PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
            destinationConnectionSpecificationId.toString(),
            DestinationConnectionSpecification.class);

    final JsonNode schemaJson =
        objectMapper.valueToTree(destinationConnectionSpecification.getSpecification());
    final JsonNode configJson = objectMapper.valueToTree(configuration);

    jsonSchemaValidation.validateThrow(schemaJson, configJson);
  }
}
