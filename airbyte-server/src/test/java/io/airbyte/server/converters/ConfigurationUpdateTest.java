/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.converters;

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
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigurationUpdateTest {

  private static final String IMAGE_REPOSITORY = "foo";
  private static final String IMAGE_TAG = "bar";
  private static final String IMAGE_NAME = IMAGE_REPOSITORY + ":" + IMAGE_TAG;
  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final JsonNode SPEC = CatalogHelpers.fieldsToJsonSchema(
      Field.of("username", JsonSchemaPrimitive.STRING),
      Field.of("password", JsonSchemaPrimitive.STRING));
  private static final ConnectorSpecification CONNECTOR_SPECIFICATION = new ConnectorSpecification().withConnectionSpecification(SPEC);
  private static final JsonNode ORIGINAL_CONFIGURATION = Jsons.jsonNode(ImmutableMap.builder()
      .put("username", "airbyte")
      .put("password", "abc")
      .build());
  private static final JsonNode NEW_CONFIGURATION = Jsons.jsonNode(ImmutableMap.builder()
      .put("username", "airbyte")
      .put("password", "xyz")
      .build());
  private static final StandardSourceDefinition SOURCE_DEFINITION = new StandardSourceDefinition()
      .withDockerRepository(IMAGE_REPOSITORY)
      .withDockerImageTag(IMAGE_TAG);
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
      .withDockerImageTag(IMAGE_TAG);
  private static final DestinationConnection ORIGINAL_DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(UUID1)
      .withDestinationDefinitionId(UUID2)
      .withConfiguration(ORIGINAL_CONFIGURATION);
  private static final DestinationConnection NEW_DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(UUID1)
      .withDestinationDefinitionId(UUID2)
      .withConfiguration(NEW_CONFIGURATION);

  private ConfigRepository configRepository;
  private SpecFetcher specFetcher;
  private JsonSecretsProcessor secretsProcessor;
  private ConfigurationUpdate configurationUpdate;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    specFetcher = mock(SpecFetcher.class);
    secretsProcessor = mock(JsonSecretsProcessor.class);

    configurationUpdate = new ConfigurationUpdate(configRepository, specFetcher, secretsProcessor);
  }

  @Test
  void testSourceUpdate() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(configRepository.getSourceConnection(UUID1)).thenReturn(ORIGINAL_SOURCE_CONNECTION);
    when(configRepository.getStandardSourceDefinition(UUID2)).thenReturn(SOURCE_DEFINITION);
    when(specFetcher.execute(IMAGE_NAME)).thenReturn(CONNECTOR_SPECIFICATION);
    when(secretsProcessor.copySecrets(ORIGINAL_CONFIGURATION, NEW_CONFIGURATION, SPEC)).thenReturn(NEW_CONFIGURATION);

    final SourceConnection actual = configurationUpdate.source(UUID1, NEW_CONFIGURATION);

    assertEquals(NEW_SOURCE_CONNECTION, actual);
  }

  @Test
  void testDestinationUpdate() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(configRepository.getDestinationConnection(UUID1)).thenReturn(ORIGINAL_DESTINATION_CONNECTION);
    when(configRepository.getStandardDestinationDefinition(UUID2)).thenReturn(DESTINATION_DEFINITION);
    when(specFetcher.execute(IMAGE_NAME)).thenReturn(CONNECTOR_SPECIFICATION);
    when(secretsProcessor.copySecrets(ORIGINAL_CONFIGURATION, NEW_CONFIGURATION, SPEC)).thenReturn(NEW_CONFIGURATION);

    final DestinationConnection actual = configurationUpdate.destination(UUID1, NEW_CONFIGURATION);

    assertEquals(NEW_DESTINATION_CONNECTION, actual);
  }

}
