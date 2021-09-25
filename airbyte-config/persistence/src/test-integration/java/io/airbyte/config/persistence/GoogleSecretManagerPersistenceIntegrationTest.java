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

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.cloud.secretmanager.v1.SecretName;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.persistence.split_secrets.GoogleSecretManagerPersistence;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import java.io.IOException;
import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class GoogleSecretManagerPersistenceIntegrationTest {

  private GoogleSecretManagerPersistence persistence;
  private String baseCoordinate;

  @BeforeEach
  void setUp() {
    final var configs = new EnvConfigs();
    persistence = GoogleSecretManagerPersistence.getEphemeral(
        configs.getSecretStoreGcpProjectId(),
        configs.getSecretStoreGcpCredentials());
    baseCoordinate = "GoogleSecretManagerPersistenceIntegrationTest_coordinate_" + RandomUtils.nextInt() % 20000;
  }

  @AfterEach
  void tearDown() throws IOException {
    final var configs = new EnvConfigs();
    try (final var client = GoogleSecretManagerPersistence.getSecretManagerServiceClient(configs.getSecretStoreGcpCredentials())) {
      // try to delete this so we aren't charged for the secret
      // if this is missed due to some sort of failure the secret will be deleted after the ttl
      client.deleteSecret(SecretName.of(
          configs.getSecretStoreGcpProjectId(),
          baseCoordinate));
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
    persistence.write(coordinate2, firstPayload);
    final var thirdRead = persistence.read(coordinate2);
    assertTrue(thirdRead.isPresent());
    assertEquals(secondPayload, thirdRead.get());
  }

}
