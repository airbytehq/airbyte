/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.persistence.MockData.HMAC_SECRET_PAYLOAD_1;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SecretsRepositoryReaderTest {

  private static final UUID UUID1 = UUID.randomUUID();

  private static final SecretCoordinate COORDINATE = new SecretCoordinate("pointer", 2);
  private static final String SECRET = "abc";
  private static final JsonNode PARTIAL_CONFIG =
      Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": { \"_secret\": \"%s\" } }", COORDINATE.getFullCoordinate()));
  private static final JsonNode FULL_CONFIG = Jsons.deserialize(String.format("{ \"username\": \"airbyte\", \"password\": \"%s\"}", SECRET));
  private static final String KEY = "_secret";
  private static final String SERVICE_ACCT_EMAIL = "a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com";
  private static final String SERVICE_ACCT_ID = "a1e5ac98-7531-48e1-943b-b46636";

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
  void testReadingServiceAccount() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final RealSecretsHydrator realSecretsHydrator = new RealSecretsHydrator(secretPersistence);
    final SecretsRepositoryReader secretsRepositoryReader =
        spy(new SecretsRepositoryReader(configRepository, realSecretsHydrator));

    final UUID workspaceId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");

    final String jsonSecretPayload = MockData.MOCK_SERVICE_ACCOUNT_1;

    final SecretCoordinate secretCoordinateHmac = new SecretCoordinate(
        "service_account_hmac_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    final SecretCoordinate secretCoordinateJson = new SecretCoordinate(
        "service_account_json_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_6b894c2b-71dc-4481-bd9f-572402643cf9", 1);

    doReturn(new WorkspaceServiceAccount().withWorkspaceId(workspaceId).withHmacKey(Jsons.jsonNode(
        Map.of(KEY, secretCoordinateHmac.getFullCoordinate()))).withJsonCredential(Jsons.jsonNode(
            Map.of(KEY, secretCoordinateJson.getFullCoordinate())))
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL)
        .withServiceAccountId(SERVICE_ACCT_ID))
            .when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);

    doReturn(Optional.of(HMAC_SECRET_PAYLOAD_1.toString())).when(secretPersistence).read(secretCoordinateHmac);

    doReturn(Optional.of(jsonSecretPayload)).when(secretPersistence).read(secretCoordinateJson);

    final WorkspaceServiceAccount actual = secretsRepositoryReader.getWorkspaceServiceAccountWithSecrets(workspaceId);
    final WorkspaceServiceAccount expected = new WorkspaceServiceAccount().withWorkspaceId(workspaceId)
        .withJsonCredential(Jsons.deserialize(jsonSecretPayload)).withHmacKey(HMAC_SECRET_PAYLOAD_1)
        .withServiceAccountId(SERVICE_ACCT_ID)
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL);
    assertEquals(expected, actual);
  }

  @Test
  void testReadingServiceAccountWithJsonNull() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final RealSecretsHydrator realSecretsHydrator = new RealSecretsHydrator(secretPersistence);
    final SecretsRepositoryReader secretsRepositoryReader =
        spy(new SecretsRepositoryReader(configRepository, realSecretsHydrator));

    final UUID workspaceId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");

    final SecretCoordinate secretCoordinateHmac = new SecretCoordinate(
        "service_account_hmac_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_e86e2eab-af9b-42a3-b074-b923b4fa617e", 1);

    doReturn(new WorkspaceServiceAccount().withWorkspaceId(workspaceId).withHmacKey(Jsons.jsonNode(
        Map.of(KEY, secretCoordinateHmac.getFullCoordinate())))
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL)
        .withServiceAccountId(SERVICE_ACCT_ID))
            .when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);

    doReturn(Optional.of(HMAC_SECRET_PAYLOAD_1.toString())).when(secretPersistence).read(secretCoordinateHmac);

    final WorkspaceServiceAccount actual = secretsRepositoryReader.getWorkspaceServiceAccountWithSecrets(workspaceId);
    final WorkspaceServiceAccount expected = new WorkspaceServiceAccount().withWorkspaceId(workspaceId)
        .withHmacKey(HMAC_SECRET_PAYLOAD_1)
        .withServiceAccountId(SERVICE_ACCT_ID)
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL);
    assertEquals(expected, actual);
  }

  @Test
  void testReadingServiceAccountWithHmacNull() throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final SecretPersistence secretPersistence = mock(SecretPersistence.class);
    final RealSecretsHydrator realSecretsHydrator = new RealSecretsHydrator(secretPersistence);
    final SecretsRepositoryReader secretsRepositoryReader =
        spy(new SecretsRepositoryReader(configRepository, realSecretsHydrator));

    final UUID workspaceId = UUID.fromString("13fb9a84-6bfa-4801-8f5e-ce717677babf");

    final String jsonSecretPayload = MockData.MOCK_SERVICE_ACCOUNT_1;

    final SecretCoordinate secretCoordinateJson = new SecretCoordinate(
        "service_account_json_13fb9a84-6bfa-4801-8f5e-ce717677babf_secret_6b894c2b-71dc-4481-bd9f-572402643cf9", 1);

    doReturn(new WorkspaceServiceAccount().withWorkspaceId(workspaceId).withJsonCredential(Jsons.jsonNode(
        Map.of(KEY, secretCoordinateJson.getFullCoordinate())))
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL)
        .withServiceAccountId(SERVICE_ACCT_ID))
            .when(configRepository).getWorkspaceServiceAccountNoSecrets(workspaceId);

    doReturn(Optional.of(jsonSecretPayload)).when(secretPersistence).read(secretCoordinateJson);

    final WorkspaceServiceAccount actual = secretsRepositoryReader.getWorkspaceServiceAccountWithSecrets(workspaceId);
    final WorkspaceServiceAccount expected = new WorkspaceServiceAccount().withWorkspaceId(workspaceId)
        .withJsonCredential(Jsons.deserialize(jsonSecretPayload))
        .withServiceAccountId(SERVICE_ACCT_ID)
        .withServiceAccountEmail(SERVICE_ACCT_EMAIL);
    assertEquals(expected, actual);
  }

}
