/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigurationUpdateTest {

  private static final String IMAGE_REPOSITORY = "foo";
  private static final String IMAGE_TAG = "bar";
  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final JsonNode SPEC = CatalogHelpers.fieldsToJsonSchema(
      Field.of(JdbcUtils.USERNAME_KEY, JsonSchemaType.STRING),
      Field.of(JdbcUtils.PASSWORD_KEY, JsonSchemaType.STRING));
  private static final ConnectorSpecification CONNECTOR_SPECIFICATION = new ConnectorSpecification().withConnectionSpecification(SPEC);
  private static final JsonNode ORIGINAL_CONFIGURATION = Jsons.jsonNode(ImmutableMap.builder()
      .put(JdbcUtils.USERNAME_KEY, "airbyte")
      .put(JdbcUtils.PASSWORD_KEY, "abc")
      .build());
  private static final JsonNode NEW_CONFIGURATION = Jsons.jsonNode(ImmutableMap.builder()
      .put(JdbcUtils.USERNAME_KEY, "airbyte")
      .put(JdbcUtils.PASSWORD_KEY, "xyz")
      .build());
  private static final StandardSourceDefinition SOURCE_DEFINITION = new StandardSourceDefinition()
      .withDockerRepository(IMAGE_REPOSITORY)
      .withDockerImageTag(IMAGE_TAG)
      .withSpec(CONNECTOR_SPECIFICATION);
  private static final SourceConnection ORIGINAL_SOURCE_CONNECTION = new SourceConnection()
      .withSourceId(UUID1)
      .withSourceDefinitionId(UUID2)
      .withConfiguration(ORIGINAL_CONFIGURATION);
  private static final SourceConnection NEW_SOURCE_CONNECTION = new SourceConnection()
      .withSourceId(UUID1)
      .withSourceDefinitionId(UUID2)
      .withConfiguration(NEW_CONFIGURATION);
  private static final StandardDestinationDefinition DESTINATION_DEFINITION = new StandardDestinationDefinition()
      .withDockerRepository(IMAGE_REPOSITORY)
      .withDockerImageTag(IMAGE_TAG)
      .withSpec(CONNECTOR_SPECIFICATION);
  private static final DestinationConnection ORIGINAL_DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(UUID1)
      .withDestinationDefinitionId(UUID2)
      .withConfiguration(ORIGINAL_CONFIGURATION);
  private static final DestinationConnection NEW_DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(UUID1)
      .withDestinationDefinitionId(UUID2)
      .withConfiguration(NEW_CONFIGURATION);

  private ConfigRepository configRepository;
  private SecretsRepositoryReader secretsRepositoryReader;
  private JsonSecretsProcessor secretsProcessor;
  private ConfigurationUpdate configurationUpdate;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    secretsRepositoryReader = mock(SecretsRepositoryReader.class);
    secretsProcessor = mock(JsonSecretsProcessor.class);

    configurationUpdate = new ConfigurationUpdate(configRepository, secretsRepositoryReader, secretsProcessor);
  }

  @Test
  void testSourceUpdate() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(secretsRepositoryReader.getSourceConnectionWithSecrets(UUID1)).thenReturn(ORIGINAL_SOURCE_CONNECTION);
    when(configRepository.getStandardSourceDefinition(UUID2)).thenReturn(SOURCE_DEFINITION);
    when(secretsProcessor.copySecrets(ORIGINAL_CONFIGURATION, NEW_CONFIGURATION, SPEC)).thenReturn(NEW_CONFIGURATION);

    final SourceConnection actual = configurationUpdate.source(UUID1, ORIGINAL_SOURCE_CONNECTION.getName(), NEW_CONFIGURATION);

    assertEquals(NEW_SOURCE_CONNECTION, actual);
  }

  @Test
  void testDestinationUpdate() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(secretsRepositoryReader.getDestinationConnectionWithSecrets(UUID1)).thenReturn(ORIGINAL_DESTINATION_CONNECTION);
    when(configRepository.getStandardDestinationDefinition(UUID2)).thenReturn(DESTINATION_DEFINITION);
    when(secretsProcessor.copySecrets(ORIGINAL_CONFIGURATION, NEW_CONFIGURATION, SPEC)).thenReturn(NEW_CONFIGURATION);

    final DestinationConnection actual = configurationUpdate.destination(UUID1, ORIGINAL_DESTINATION_CONNECTION.getName(), NEW_CONFIGURATION);

    assertEquals(NEW_DESTINATION_CONNECTION, actual);
  }

}
