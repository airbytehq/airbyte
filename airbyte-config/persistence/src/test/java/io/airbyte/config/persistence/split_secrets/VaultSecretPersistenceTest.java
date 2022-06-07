package io.airbyte.config.persistence.split_secrets;

import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.vault.VaultContainer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class VaultSecretPersistenceTest {
  private VaultSecretPersistence persistence;
  private String baseCoordinate;

  private VaultContainer vaultContainer;

  @BeforeEach
  void setUp() {
    vaultContainer = new VaultContainer("vault").withVaultToken("vault-dev-token-id");
    vaultContainer.start();

    final var vaultAddress = "http://" + vaultContainer.getHost() + ":" + vaultContainer.getFirstMappedPort();

    persistence = new VaultSecretPersistence(vaultAddress, "secret/testing", "vault-dev-token-id");
    baseCoordinate = "VaultSecretPersistenceIntegrationTest_coordinate_" + RandomUtils.nextInt() % 20000;
  }

  @AfterEach
  void tearDown() {
    vaultContainer.stop();
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

