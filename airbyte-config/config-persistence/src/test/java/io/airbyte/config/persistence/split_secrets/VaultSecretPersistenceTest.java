/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import lombok.val;
import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.vault.VaultContainer;

class VaultSecretPersistenceTest {

  private VaultSecretPersistence persistence;
  private String baseCoordinate;

  private VaultContainer vaultContainer;

  @BeforeEach
  void setUp() {
    vaultContainer = new VaultContainer("vault").withVaultToken("vault-dev-token-id");
    vaultContainer.start();

    val vaultAddress = "http://" + vaultContainer.getHost() + ":" + vaultContainer.getFirstMappedPort();

    persistence = new VaultSecretPersistence(vaultAddress, "secret/testing", "vault-dev-token-id");
    baseCoordinate = "VaultSecretPersistenceIntegrationTest_coordinate_" + RandomUtils.nextInt() % 20000;
  }

  @AfterEach
  void tearDown() {
    vaultContainer.stop();
  }

  @Test
  void testReadWriteUpdate() {
    val coordinate1 = new SecretCoordinate(baseCoordinate, 1);

    // try reading non-existent value
    val firstRead = persistence.read(coordinate1);
    assertThat(firstRead.isEmpty()).isTrue();

    // write
    val firstPayload = "abc";
    persistence.write(coordinate1, firstPayload);
    val secondRead = persistence.read(coordinate1);
    assertThat(secondRead.isPresent()).isTrue();
    assertEquals(firstPayload, secondRead.get());

    // update
    val secondPayload = "def";
    val coordinate2 = new SecretCoordinate(baseCoordinate, 2);
    persistence.write(coordinate2, secondPayload);
    val thirdRead = persistence.read(coordinate2);
    assertThat(thirdRead.isPresent()).isTrue();
    assertEquals(secondPayload, thirdRead.get());
  }

}
