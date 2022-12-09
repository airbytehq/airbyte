/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import java.util.Optional;
import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class AWSSecretManagerPersistenceIntegrationTest {

  public String coordinate_base;
  private AWSSecretManagerPersistence persistence;
  private final Configs configs = new EnvConfigs();

  @BeforeEach
  void setup() {
    persistence = new AWSSecretManagerPersistence(configs.getAwsAccessKey(), configs.getAwsSecretAccessKey());
    coordinate_base = "aws/airbyte/secret/integration/" + RandomUtils.nextInt() % 20000;
  }

  @Test
  void testReadWriteUpdate() throws InterruptedException {
    SecretCoordinate secretCoordinate = new SecretCoordinate(coordinate_base, 1);

    // try reading a non-existent secret
    Optional<String> firstRead = persistence.read(secretCoordinate);
    assertTrue(firstRead.isEmpty());

    // write it
    String payload = "foo-secret";
    persistence.write(secretCoordinate, payload);
    persistence.cache.refreshNow(secretCoordinate.getCoordinateBase());
    Optional<String> read2 = persistence.read(secretCoordinate);
    assertTrue(read2.isPresent());
    assertEquals(payload, read2.get());

    // update it
    final var secondPayload = "bar-secret";
    final var coordinate2 = new SecretCoordinate(coordinate_base, 2);
    persistence.write(coordinate2, secondPayload);
    persistence.cache.refreshNow(secretCoordinate.getCoordinateBase());
    final var thirdRead = persistence.read(coordinate2);
    assertTrue(thirdRead.isPresent());
    assertEquals(secondPayload, thirdRead.get());
  }

  @AfterEach
  void tearDown() {
    persistence.deleteSecret(new SecretCoordinate(coordinate_base, 1));
  }

}
