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

package io.airbyte.config.persistence.split_secrets;

import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.io.IOException;
import java.util.Optional;

/**
 * Provides the ability to read and write secrets to a backing store. Assumes that secret payloads
 * are always strings. See {@link SecretCoordinate} for more information on how secrets are
 * identified.
 */
public interface SecretPersistence {

  Optional<String> read(final SecretCoordinate coordinate);

  void write(final SecretCoordinate coordinate, final String payload) throws IllegalArgumentException;

  static Optional<SecretPersistence> getLongLived(Configs configs) throws IOException {
    switch (configs.getSecretPersistenceType()) {
      case TESTING_CONFIG_DB_TABLE -> {
        final Database configDatabase = new ConfigsDatabaseInstance(
            configs.getConfigDatabaseUser(),
            configs.getConfigDatabasePassword(),
            configs.getConfigDatabaseUrl())
                .getAndInitialize();

        return Optional.of(new LocalTestingSecretPersistence(configDatabase));
      }
      case GOOGLE_SECRET_MANAGER -> {
        return Optional.of(GoogleSecretManagerPersistence.getLongLived(configs.getSecretStoreGcpProjectId(), configs.getSecretStoreGcpProjectId()));
      }
      default -> {
        return Optional.empty();
      }
    }
  }

  static Optional<SecretPersistence> getEphemeral(Configs configs) throws IOException {
    switch (configs.getSecretPersistenceType()) {
      case TESTING_CONFIG_DB_TABLE -> {
        final Database configDatabase = new ConfigsDatabaseInstance(
            configs.getConfigDatabaseUser(),
            configs.getConfigDatabasePassword(),
            configs.getConfigDatabaseUrl())
                .getAndInitialize();

        return Optional.of(new LocalTestingSecretPersistence(configDatabase));
      }
      case GOOGLE_SECRET_MANAGER -> {
        return Optional.of(GoogleSecretManagerPersistence.getEphemeral(configs.getSecretStoreGcpProjectId(), configs.getSecretStoreGcpProjectId()));
      }
      default -> {
        return Optional.empty();
      }
    }
  }

}
