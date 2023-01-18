/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import java.util.Optional;
import javax.annotation.Nullable;
import org.jooq.DSLContext;

/**
 * Provides the ability to read and write secrets to a backing store. Assumes that secret payloads
 * are always strings. See {@link SecretCoordinate} for more information on how secrets are
 * identified.
 */
@SuppressWarnings("PMD.MissingOverride")
public interface SecretPersistence extends ReadOnlySecretPersistence {

  /**
   * Performs any initialization prior to utilization of the persistence object. This exists to make
   * it possible to create instances within a dependency management framework, where any
   * initialization logic should not be present in a constructor.
   *
   * @throws Exception if unable to perform the initialization.
   */
  default void initialize() throws Exception {}

  Optional<String> read(final SecretCoordinate coordinate);

  void write(final SecretCoordinate coordinate, final String payload);

  static Optional<SecretPersistence> getLongLived(final @Nullable DSLContext dslContext, final Configs configs) {
    switch (configs.getSecretPersistenceType()) {
      case TESTING_CONFIG_DB_TABLE -> {
        final Database configDatabase = new Database(dslContext);
        return Optional.of(new LocalTestingSecretPersistence(configDatabase));
      }
      case GOOGLE_SECRET_MANAGER -> {
        return Optional.of(GoogleSecretManagerPersistence.getLongLived(configs.getSecretStoreGcpProjectId(), configs.getSecretStoreGcpCredentials()));
      }
      case VAULT -> {
        return Optional.of(new VaultSecretPersistence(configs.getVaultAddress(), configs.getVaultPrefix(), configs.getVaultToken()));
      }
      case AWS_SECRET_MANAGER -> {
        return Optional.of(new AWSSecretManagerPersistence(configs.getAwsAccessKey(), configs.getAwsSecretAccessKey()));
      }
      default -> {
        return Optional.empty();
      }
    }
  }

  static SecretsHydrator getSecretsHydrator(final @Nullable DSLContext dslContext, final Configs configs) {
    final var persistence = getLongLived(dslContext, configs);

    if (persistence.isPresent()) {
      return new RealSecretsHydrator(persistence.get());
    } else {
      return new NoOpSecretsHydrator();
    }
  }

  static Optional<SecretPersistence> getEphemeral(final DSLContext dslContext, final Configs configs) {
    switch (configs.getSecretPersistenceType()) {
      case TESTING_CONFIG_DB_TABLE -> {
        final Database configDatabase = new Database(dslContext);
        return Optional.of(new LocalTestingSecretPersistence(configDatabase));
      }
      case GOOGLE_SECRET_MANAGER -> {
        return Optional.of(GoogleSecretManagerPersistence.getEphemeral(configs.getSecretStoreGcpProjectId(), configs.getSecretStoreGcpCredentials()));
      }
      case VAULT -> {
        return Optional.of(new VaultSecretPersistence(configs.getVaultAddress(), configs.getVaultPrefix(), configs.getVaultToken()));
      }
      case AWS_SECRET_MANAGER -> {
        return Optional.of(new AWSSecretManagerPersistence(configs.getAwsAccessKey(), configs.getAwsSecretAccessKey()));
      }
      default -> {
        return Optional.empty();
      }
    }
  }

}
