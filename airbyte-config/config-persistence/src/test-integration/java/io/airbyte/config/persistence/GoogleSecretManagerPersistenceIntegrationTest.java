/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.api.gax.rpc.NotFoundException;
import com.google.cloud.secretmanager.v1.SecretName;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.persistence.split_secrets.GoogleSecretManagerPersistence;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import java.io.IOException;
import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Triggered as part of integration tests in CI. It uses credentials in Github to connect to the
 * integration testing GCP project.
 */
@SuppressWarnings("PMD.EmptyCatchBlock")
class GoogleSecretManagerPersistenceIntegrationTest {

  private GoogleSecretManagerPersistence persistence;
  private String baseCoordinate;
  private final Configs configs = new EnvConfigs();

  @BeforeEach
  void setUp() {
    persistence = GoogleSecretManagerPersistence.getEphemeral(
        configs.getSecretStoreGcpProjectId(),
        configs.getSecretStoreGcpCredentials());
    baseCoordinate = "GoogleSecretManagerPersistenceIntegrationTest_coordinate_" + RandomUtils.nextInt() % 20000;
  }

  @AfterEach
  void tearDown() throws IOException {
    try (final var client = GoogleSecretManagerPersistence.getSecretManagerServiceClient(configs.getSecretStoreGcpCredentials())) {
      // try to delete this so we aren't charged for the secret
      // if this is missed due to some sort of failure the secret will be deleted after the ttl
      try {
        client.deleteSecret(SecretName.of(
            configs.getSecretStoreGcpProjectId(),
            baseCoordinate));
      } catch (final NotFoundException nfe) {
        // do nothing
      }
    }
  }

  @Test
  void testReadWriteUpdate() {
    final var coordinate1 = new SecretCoordinate(baseCoordinate, 1);

    // try reading non-existent value
    final var firstRead = persistence.read(coordinate1);
    assertTrue(firstRead.isEmpty());

    // write
    final var firstPayload = "abc";
    persistence.write(coordinate1, firstPayload);
    final var secondRead = persistence.read(coordinate1);
    assertTrue(secondRead.isPresent());
    assertEquals(firstPayload, secondRead.get());

    // update
    final var secondPayload = "def";
    final var coordinate2 = new SecretCoordinate(baseCoordinate, 2);
    persistence.write(coordinate2, secondPayload);
    final var thirdRead = persistence.read(coordinate2);
    assertTrue(thirdRead.isPresent());
    assertEquals(secondPayload, thirdRead.get());
  }

}
