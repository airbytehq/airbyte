/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.persistence.MockData.HMAC_SECRET_PAYLOAD_1;
import static io.airbyte.config.persistence.MockData.HMAC_SECRET_PAYLOAD_2;
import static io.airbyte.config.persistence.MockData.MOCK_SERVICE_ACCOUNT_1;
import static io.airbyte.config.persistence.MockData.MOCK_SERVICE_ACCOUNT_2;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

@SuppressWarnings({"PMD.AvoidThrowingRawExceptionTypes", "PMD.UnusedPrivateField"})
class SecretsRepositoryWriterTest {

  private static final UUID UUID1 = UUID.randomUUID();

  private static final ConnectorSpecification SPEC = new ConnectorSpecification()
      .withConnectionSpecification(Jsons.deserialize(
          "{ \"properties\": { \"username\": { \"type\": \"string\" }, \"password\": { \"type\": \"string\", \"airbyte_secret\": true } } }"));

  private static final String SECRET = "abc";
  private static final JsonNode FULL_CONFIG = Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": \"%s\"}", SECRET));

  private static final SourceConnection SOURCE_WITH_FULL_CONFIG = new SourceConnection()
      .withSourceId(UUID1)
      .withSourceDefinitionId(UUID.randomUUID())
      .withConfiguration(FULL_CONFIG);

  private static final DestinationConnection DESTINATION_WITH_FULL_CONFIG = new DestinationConnection()
      .withDestinationId(UUID1)
      .withConfiguration(FULL_CONFIG);

  private static final StandardSourceDefinition SOURCE_DEF = new StandardSourceDefinition()
      .withSourceDefinitionId(SOURCE_WITH_FULL_CONFIG.getSourceDefinitionId())
      .withSpec(SPEC);

  private static final StandardDestinationDefinition DEST_DEF = new StandardDestinationDefinition()
      .withDestinationDefinitionId(DESTINATION_WITH_FULL_CONFIG.getDestinationDefinitionId())
      .withSpec(SPEC);

  private static final String PASSWORD_PROPERTY_NAME = "password";
  private static final String PASSWORD_FIELD_NAME = "_secret";

  private ConfigRepository configRepository;
  private MemorySecretPersistence longLivedSecretPersistence;
  private MemorySecretPersistence ephemeralSecretPersistence;
  private SecretsRepositoryWriter secretsRepositoryWriter;

  private RealSecretsHydrator longLivedSecretsHydrator;
  private SecretsRepositoryReader longLivedSecretsRepositoryReader;
  private RealSecretsHydrator ephemeralSecretsHydrator;
  private SecretsRepositoryReader ephemeralSecretsRepositoryReader;

  @BeforeEach
  void setup() {
    configRepository = spy(mock(ConfigRepository.class));
    longLivedSecretPersistence = new MemorySecretPersistence();
    ephemeralSecretPersistence = new MemorySecretPersistence();

    secretsRepositoryWriter = new SecretsRepositoryWriter(
        configRepository,
        Optional.of(longLivedSecretPersistence),
        Optional.of(ephemeralSecretPersistence));

    longLivedSecretsHydrator = new RealSecretsHydrator(longLivedSecretPersistence);
    longLivedSecretsRepositoryReader = new SecretsRepositoryReader(configRepository, longLivedSecretsHydrator);

    ephemeralSecretsHydrator = new RealSecretsHydrator(ephemeralSecretPersistence);
    ephemeralSecretsRepositoryReader = new SecretsRepositoryReader(configRepository, ephemeralSecretsHydrator);
  }

  @Test
  void testWriteSourceConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    doThrow(ConfigNotFoundException.class).when(configRepository).getSourceConnection(UUID1);

    secretsRepositoryWriter.writeSourceConnection(SOURCE_WITH_FULL_CONFIG, SPEC);
    final SecretCoordinate coordinate = getCoordinateFromSecretsStore(longLivedSecretPersistence);

    assertNotNull(coordinate);
    final SourceConnection partialSource = injectCoordinateIntoSource(coordinate.getFullCoordinate());
    verify(configRepository).writeSourceConnectionNoSecrets(partialSource);
    final Optional<String> persistedSecret = longLivedSecretPersistence.read(coordinate);
    assertTrue(persistedSecret.isPresent());
    assertEquals(SECRET, persistedSecret.get());

    // verify that the round trip works.
    reset(configRepository);
    when(configRepository.getSourceConnection(UUID1)).thenReturn(partialSource);
    assertEquals(SOURCE_WITH_FULL_CONFIG, longLivedSecretsRepositoryReader.getSourceConnectionWithSecrets(UUID1));
  }

  @Test
  void testWriteDestinationConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    doThrow(ConfigNotFoundException.class).when(configRepository).getDestinationConnection(UUID1);

    secretsRepositoryWriter.writeDestinationConnection(DESTINATION_WITH_FULL_CONFIG, SPEC);
    final SecretCoordinate coordinate = getCoordinateFromSecretsStore(longLivedSecretPersistence);

    assertNotNull(coordinate);
    final DestinationConnection partialDestination = injectCoordinateIntoDestination(coordinate.getFullCoordinate());
    verify(configRepository).writeDestinationConnectionNoSecrets(partialDestination);
    final Optional<String> persistedSecret = longLivedSecretPersistence.read(coordinate);
    assertTrue(persistedSecret.isPresent());
    assertEquals(SECRET, persistedSecret.get());

    // verify that the round trip works.
    reset(configRepository);
    when(configRepository.getDestinationConnection(UUID1)).thenReturn(partialDestination);
    assertEquals(DESTINATION_WITH_FULL_CONFIG, longLivedSecretsRepositoryReader.getDestinationConnectionWithSecrets(UUID1));
  }

  @Test
  void testStatefulSplitEphemeralSecrets() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode split = secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        SOURCE_WITH_FULL_CONFIG.getConfiguration(),
        SPEC);
    final SecretCoordinate coordinate = getCoordinateFromSecretsStore(ephemeralSecretPersistence);

    assertNotNull(coordinate);
    final Optional<String> persistedSecret = ephemeralSecretPersistence.read(coordinate);
    assertTrue(persistedSecret.isPresent());
    assertEquals(SECRET, persistedSecret.get());

    // verify that the round trip works.
    assertEquals(SOURCE_WITH_FULL_CONFIG.getConfiguration(), ephemeralSecretsHydrator.hydrate(split));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testReplaceAllConfigs() throws IOException {
    final Map<AirbyteConfig, Stream<?>> configs = new HashMap<>();
    configs.put(ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(Jsons.clone(SOURCE_DEF)));
    configs.put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, Stream.of(Jsons.clone(DEST_DEF)));
    configs.put(ConfigSchema.SOURCE_CONNECTION, Stream.of(Jsons.clone(SOURCE_WITH_FULL_CONFIG)));
    configs.put(ConfigSchema.DESTINATION_CONNECTION, Stream.of(Jsons.clone(DESTINATION_WITH_FULL_CONFIG)));

    secretsRepositoryWriter.replaceAllConfigs(configs, false);

    final ArgumentCaptor<Map<AirbyteConfig, Stream<?>>> argument = ArgumentCaptor.forClass(Map.class);
    verify(configRepository).replaceAllConfigsNoSecrets(argument.capture(), eq(false));
    final Map<AirbyteConfig, ? extends List<?>> actual = argument.getValue().entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> e.getValue().collect(Collectors.toList())));

    assertEquals(SOURCE_DEF, actual.get(ConfigSchema.STANDARD_SOURCE_DEFINITION).get(0));
    assertEquals(DEST_DEF, actual.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION).get(0));

    // we can't easily get the pointer, so verify the secret has been stripped out and then make sure
    // the rest of the object meets expectations.
    final SourceConnection actualSource = (SourceConnection) actual.get(ConfigSchema.SOURCE_CONNECTION).get(0);
    assertTrue(actualSource.getConfiguration().get(PASSWORD_PROPERTY_NAME).has(PASSWORD_FIELD_NAME));
    ((ObjectNode) actualSource.getConfiguration()).remove(PASSWORD_PROPERTY_NAME);
    final SourceConnection expectedSource = Jsons.clone(SOURCE_WITH_FULL_CONFIG);
    ((ObjectNode) expectedSource.getConfiguration()).remove(PASSWORD_PROPERTY_NAME);
    assertEquals(expectedSource, actualSource);

    final DestinationConnection actualDest = (DestinationConnection) actual.get(ConfigSchema.DESTINATION_CONNECTION).get(0);
    assertTrue(actualDest.getConfiguration().get(PASSWORD_PROPERTY_NAME).has(PASSWORD_FIELD_NAME));
    ((ObjectNode) actualDest.getConfiguration()).remove(PASSWORD_PROPERTY_NAME);
    final DestinationConnection expectedDest = Jsons.clone(DESTINATION_WITH_FULL_CONFIG);
    ((ObjectNode) expectedDest.getConfiguration()).remove(PASSWORD_PROPERTY_NAME);
    assertEquals(expectedDest, actualDest);
  }

  // this only works if the secrets store has one secret.
  private SecretCoordinate getCoordinateFromSecretsStore(final MemorySecretPersistence secretPersistence) {
    return secretPersistence.getMap()
        .keySet()
        .stream()
        .findFirst()
        .orElse(null);
  }

  private static JsonNode injectCoordinate(final String coordinate) {
    return Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": { \"_secret\": \"%s\" } }", coordinate));
  }

  private static SourceConnection injectCoordinateIntoSource(final String coordinate) {
    return Jsons.clone(SOURCE_WITH_FULL_CONFIG).withConfiguration(injectCoordinate(coordinate));
  }

  private static DestinationConnection injectCoordinateIntoDestination(final String coordinate) {
    return Jsons.clone(DESTINATION_WITH_FULL_CONFIG).withConfiguration(injectCoordinate(coordinate));
  }

  @Test
  void testWriteWorkspaceServiceAccount() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID workspaceId = UUID.randomUUID();

    final String jsonSecretPayload = MOCK_SERVICE_ACCOUNT_1;
    final WorkspaceServiceAccount workspaceServiceAccount = new WorkspaceServiceAccount()
        .withWorkspaceId(workspaceId)
        .withHmacKey(HMAC_SECRET_PAYLOAD_1)
        .withServiceAccountId("a1e5ac98-7531-48e1-943b-b46636")
        .withServiceAccountEmail("a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com")
        .withJsonCredential(Jsons.deserialize(jsonSecretPayload));

    doThrow(new ConfigNotFoundException(ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, workspaceId.toString()))
        .when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);
    secretsRepositoryWriter.writeServiceAccountJsonCredentials(workspaceServiceAccount);

    assertEquals(2, longLivedSecretPersistence.getMap().size());

    String jsonPayloadInPersistence = null;
    String hmacPayloadInPersistence = null;

    SecretCoordinate jsonSecretCoordinate = null;
    SecretCoordinate hmacSecretCoordinate = null;
    for (final Map.Entry<SecretCoordinate, String> entry : longLivedSecretPersistence.getMap().entrySet()) {
      if (entry.getKey().getFullCoordinate().contains("json")) {
        jsonSecretCoordinate = entry.getKey();
        jsonPayloadInPersistence = entry.getValue();
      } else if (entry.getKey().getFullCoordinate().contains("hmac")) {
        hmacSecretCoordinate = entry.getKey();
        hmacPayloadInPersistence = entry.getValue();
      } else {
        throw new RuntimeException("");
      }
    }

    assertNotNull(jsonPayloadInPersistence);
    assertNotNull(hmacPayloadInPersistence);
    assertNotNull(jsonSecretCoordinate);
    assertNotNull(hmacSecretCoordinate);

    assertEquals(jsonSecretPayload, jsonPayloadInPersistence);
    assertEquals(HMAC_SECRET_PAYLOAD_1.toString(), hmacPayloadInPersistence);

    verify(configRepository).writeWorkspaceServiceAccountNoSecrets(
        Jsons.clone(workspaceServiceAccount.withJsonCredential(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, jsonSecretCoordinate.getFullCoordinate())))
            .withHmacKey(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, hmacSecretCoordinate.getFullCoordinate())))));
  }

  @Test
  void testWriteSameStagingConfiguration() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final SecretsRepositoryWriter secretsRepositoryWriter = spy(
        new SecretsRepositoryWriter(configRepository, Optional.of(secretPersistence), Optional.of(secretPersistence)));

    final UUID workspaceId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");

    final String jsonSecretPayload = MOCK_SERVICE_ACCOUNT_1;
    final WorkspaceServiceAccount workspaceServiceAccount = new WorkspaceServiceAccount().withWorkspaceId(workspaceId).withHmacKey(
        HMAC_SECRET_PAYLOAD_1)
        .withServiceAccountId("a1e5ac98-7531-48e1-943b-b46636")
        .withServiceAccountEmail("a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com")
        .withJsonCredential(Jsons.deserialize(jsonSecretPayload));

    final SecretCoordinate jsonSecretCoordinate = new SecretCoordinate(
        "service_account_json_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    final SecretCoordinate hmacSecretCoordinate = new SecretCoordinate(
        "service_account_hmac_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    final WorkspaceServiceAccount cloned = Jsons.clone(workspaceServiceAccount)
        .withJsonCredential(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, jsonSecretCoordinate.getFullCoordinate())))
        .withHmacKey(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, hmacSecretCoordinate.getFullCoordinate())));

    doReturn(cloned).when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);

    doReturn(Optional.of(jsonSecretPayload)).when(secretPersistence).read(jsonSecretCoordinate);
    doReturn(Optional.of(HMAC_SECRET_PAYLOAD_1.toString())).when(secretPersistence).read(hmacSecretCoordinate);
    secretsRepositoryWriter.writeServiceAccountJsonCredentials(workspaceServiceAccount);

    final ArgumentCaptor<SecretCoordinate> coordinates = ArgumentCaptor.forClass(SecretCoordinate.class);
    final ArgumentCaptor<String> payloads = ArgumentCaptor.forClass(String.class);

    verify(secretPersistence, times(2)).write(coordinates.capture(), payloads.capture());
    final List<SecretCoordinate> actualCoordinates = coordinates.getAllValues();
    assertEquals(2, actualCoordinates.size());
    assertThat(actualCoordinates, containsInAnyOrder(jsonSecretCoordinate, hmacSecretCoordinate));

    final List<String> actualPayload = payloads.getAllValues();
    assertEquals(2, actualPayload.size());
    assertThat(actualPayload, containsInAnyOrder(jsonSecretPayload, HMAC_SECRET_PAYLOAD_1.toString()));

    verify(secretPersistence).write(hmacSecretCoordinate, HMAC_SECRET_PAYLOAD_1.toString());
    verify(configRepository).writeWorkspaceServiceAccountNoSecrets(
        cloned);
  }

  @Test
  void testWriteDifferentStagingConfiguration() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final SecretsRepositoryWriter secretsRepositoryWriter =
        spy(new SecretsRepositoryWriter(configRepository, Optional.of(secretPersistence), Optional.of(secretPersistence)));

    final UUID workspaceId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");

    final String jsonSecretOldPayload = MOCK_SERVICE_ACCOUNT_1;
    final String jsonSecretNewPayload = MOCK_SERVICE_ACCOUNT_2;

    final WorkspaceServiceAccount workspaceServiceAccount = new WorkspaceServiceAccount()
        .withWorkspaceId(workspaceId)
        .withHmacKey(HMAC_SECRET_PAYLOAD_2)
        .withServiceAccountId("a1e5ac98-7531-48e1-943b-b46636")
        .withServiceAccountEmail("a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com")
        .withJsonCredential(Jsons.deserialize(jsonSecretNewPayload));

    final SecretCoordinate jsonSecretOldCoordinate = new SecretCoordinate(
        "service_account_json_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    final SecretCoordinate hmacSecretOldCoordinate = new SecretCoordinate(
        "service_account_hmac_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    final WorkspaceServiceAccount cloned = Jsons.clone(workspaceServiceAccount)
        .withJsonCredential(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, jsonSecretOldCoordinate.getFullCoordinate())))
        .withHmacKey(Jsons.jsonNode(Map.of(PASSWORD_FIELD_NAME, hmacSecretOldCoordinate.getFullCoordinate())));

    doReturn(cloned).when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);

    doReturn(Optional.of(HMAC_SECRET_PAYLOAD_1.toString())).when(secretPersistence).read(hmacSecretOldCoordinate);
    doReturn(Optional.of(jsonSecretOldPayload)).when(secretPersistence).read(jsonSecretOldCoordinate);

    secretsRepositoryWriter.writeServiceAccountJsonCredentials(workspaceServiceAccount);

    final SecretCoordinate jsonSecretNewCoordinate = new SecretCoordinate(
        "service_account_json_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 2);

    final SecretCoordinate hmacSecretNewCoordinate = new SecretCoordinate(
        "service_account_hmac_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 2);

    final ArgumentCaptor<SecretCoordinate> coordinates = ArgumentCaptor.forClass(SecretCoordinate.class);
    final ArgumentCaptor<String> payloads = ArgumentCaptor.forClass(String.class);

    verify(secretPersistence, times(2)).write(coordinates.capture(), payloads.capture());
    final List<SecretCoordinate> actualCoordinates = coordinates.getAllValues();
    assertEquals(2, actualCoordinates.size());
    assertThat(actualCoordinates, containsInAnyOrder(jsonSecretNewCoordinate, hmacSecretNewCoordinate));

    final List<String> actualPayload = payloads.getAllValues();
    assertEquals(2, actualPayload.size());
    assertThat(actualPayload, containsInAnyOrder(jsonSecretNewPayload, HMAC_SECRET_PAYLOAD_2.toString()));

    verify(configRepository).writeWorkspaceServiceAccountNoSecrets(Jsons.clone(workspaceServiceAccount).withJsonCredential(Jsons.jsonNode(
        Map.of(PASSWORD_FIELD_NAME, jsonSecretNewCoordinate.getFullCoordinate()))).withHmacKey(Jsons.jsonNode(
            Map.of(PASSWORD_FIELD_NAME, hmacSecretNewCoordinate.getFullCoordinate()))));
  }

}
