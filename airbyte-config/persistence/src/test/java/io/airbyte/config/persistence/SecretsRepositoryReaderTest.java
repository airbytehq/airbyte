/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorConfigurationBinding;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.TreeMap;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SecretsRepositoryReaderTest {

  private static final UUID UUID1 = UUID.randomUUID();

  private static final SecretCoordinate COORDINATE = new SecretCoordinate("pointer", 2);
  private static final String SECRET = "abc";
  private static final JsonNode PARTIAL_CONFIG =
      Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": { \"_secret\": \"%s\" } }", COORDINATE.getFullCoordinate()));
  private static final JsonNode FULL_CONFIG = Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": \"%s\"}", SECRET));

  private static final SourceConnection SOURCE_WITH_PARTIAL_CONFIG = new SourceConnection()
      .withSourceId(UUID1)
      .withConfiguration(PARTIAL_CONFIG);
  private static final SourceConnection SOURCE_WITH_FULL_CONFIG = Jsons.clone(SOURCE_WITH_PARTIAL_CONFIG)
      .withConfiguration(FULL_CONFIG);

  private static final DestinationConnection DESTINATION_WITH_PARTIAL_CONFIG = new DestinationConnection()
      .withDestinationId(UUID1)
      .withConfiguration(PARTIAL_CONFIG);
  private static final DestinationConnection DESTINATION_WITH_FULL_CONFIG = Jsons.clone(DESTINATION_WITH_PARTIAL_CONFIG)
      .withConfiguration(FULL_CONFIG);

  private ConfigRepository configRepository;
  private SecretsRepositoryReader secretsRepositoryReader;
  private MemorySecretPersistence secretPersistence;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    secretPersistence = new MemorySecretPersistence();
    final SecretsHydrator secretsHydrator = new RealSecretsHydrator(secretPersistence);
    secretsRepositoryReader = new SecretsRepositoryReader(configRepository, secretsHydrator);
  }

  @Test
  void testGetSourceWithSecrets() throws JsonValidationException, ConfigNotFoundException, IOException {
    secretPersistence.write(COORDINATE, SECRET);
    when(configRepository.getSourceConnection(UUID1)).thenReturn(SOURCE_WITH_PARTIAL_CONFIG);
    assertEquals(SOURCE_WITH_FULL_CONFIG, secretsRepositoryReader.getSourceConnectionWithSecrets(UUID1));
  }

  @Test
  void testListSourcesWithSecrets() throws JsonValidationException, IOException {
    secretPersistence.write(COORDINATE, SECRET);
    when(configRepository.listSourceConnection()).thenReturn(List.of(SOURCE_WITH_PARTIAL_CONFIG));
    assertEquals(List.of(SOURCE_WITH_FULL_CONFIG), secretsRepositoryReader.listSourceConnectionWithSecrets());
  }

  @Test
  void testGetDestinationWithSecrets() throws JsonValidationException, ConfigNotFoundException, IOException {
    secretPersistence.write(COORDINATE, SECRET);
    when(configRepository.getDestinationConnection(UUID1)).thenReturn(DESTINATION_WITH_PARTIAL_CONFIG);
    assertEquals(DESTINATION_WITH_FULL_CONFIG, secretsRepositoryReader.getDestinationConnectionWithSecrets(UUID1));
  }

  @Test
  void testListDestinationsWithSecrets() throws JsonValidationException, IOException {
    secretPersistence.write(COORDINATE, SECRET);
    when(configRepository.listDestinationConnection()).thenReturn(List.of(DESTINATION_WITH_PARTIAL_CONFIG));
    assertEquals(List.of(DESTINATION_WITH_FULL_CONFIG), secretsRepositoryReader.listDestinationConnectionWithSecrets());
  }

  @Test
  void testDumpConfigsWithSecrets() throws IOException {
    secretPersistence.write(COORDINATE, SECRET);
    final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(UUID.randomUUID());

    final Map<String, Stream<JsonNode>> dumpFromConfigRepository = new HashMap<>();
    dumpFromConfigRepository.put(ConfigSchema.STANDARD_WORKSPACE.name(), Stream.of(Jsons.jsonNode(workspace)));
    dumpFromConfigRepository.put(ConfigSchema.SOURCE_CONNECTION.name(), Stream.of(Jsons.jsonNode(SOURCE_WITH_PARTIAL_CONFIG)));
    dumpFromConfigRepository.put(ConfigSchema.DESTINATION_CONNECTION.name(), Stream.of(Jsons.jsonNode(DESTINATION_WITH_PARTIAL_CONFIG)));
    when(configRepository.dumpConfigsNoSecrets()).thenReturn(dumpFromConfigRepository);

    final Map<String, List<JsonNode>> expected = new HashMap<>();
    expected.put(ConfigSchema.STANDARD_WORKSPACE.name(), List.of(Jsons.jsonNode(workspace)));
    expected.put(ConfigSchema.SOURCE_CONNECTION.name(), List.of(Jsons.jsonNode(SOURCE_WITH_FULL_CONFIG)));
    expected.put(ConfigSchema.DESTINATION_CONNECTION.name(), List.of(Jsons.jsonNode(DESTINATION_WITH_FULL_CONFIG)));

    final Map<String, List<JsonNode>> actual = secretsRepositoryReader.dumpConfigsWithSecrets()
        .entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> e.getValue().collect(Collectors.toList())));

    assertEquals(expected, actual);
  }

  @Test
  public void testReadStagingConfiguration() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final RealSecretsHydrator realSecretsHydrator = new RealSecretsHydrator(secretPersistence);
    final SecretsRepositoryReader secretsRepositoryReader =
        spy(new SecretsRepositoryReader(configRepository, realSecretsHydrator));

    final UUID destinationDefinitionId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");
    final JsonNode secretPayload = Jsons.jsonNode(sortMap(Map.of("name", "John", "age", "30", "car", "null")));
    assertEquals("{\"age\":\"30\",\"car\":\"null\",\"name\":\"John\"}", secretPayload.toString());

    final SecretCoordinate secretCoordinate = new SecretCoordinate(
        "destination_definition_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    doReturn(new ActorConfigurationBinding().withActorDefinitionId(destinationDefinitionId).withConfiguration(Jsons.jsonNode(
        Map.of("_secret", secretCoordinate.getFullCoordinate()))))
            .when(configRepository).getActorConfigurationBindingNoSecrets(destinationDefinitionId);
    doReturn(Optional.of(secretPayload.toString())).when(secretPersistence).read(secretCoordinate);

    final ActorConfigurationBinding actual = secretsRepositoryReader.getActorConfigurationBindingWithSecrets(destinationDefinitionId);
    final ActorConfigurationBinding expected = new ActorConfigurationBinding().withActorDefinitionId(destinationDefinitionId)
        .withConfiguration(secretPayload);
    assertEquals(expected, actual);
  }

  private Map<String, String> sortMap(Map<String, String> originalMap) {
    return originalMap.entrySet().stream()
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (oldValue, newValue) -> newValue, TreeMap::new));
  }

}
