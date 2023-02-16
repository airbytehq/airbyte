/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.persistence.split_secrets.AWSSecretManagerPersistence;
import io.airbyte.config.persistence.split_secrets.GoogleSecretManagerPersistence;
import io.airbyte.config.persistence.split_secrets.LocalTestingSecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.config.persistence.split_secrets.VaultSecretPersistence;
import io.airbyte.db.Database;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

/**
 * Micronaut bean factory for secret persistence-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class SecretPersistenceBeanFactory {

  @Singleton
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^(?!testing_config_db_table).*")
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^(?!google_secret_manager).*")
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^(?!vault).*")
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^(?!aws_secret_manager).*")
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("secretPersistence")
  public SecretPersistence defaultSecretPersistence(@Named("configDatabase") final Database configDatabase) {
    return localTestingSecretPersistence(configDatabase);
  }

  @Singleton
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^testing_config_db_table$")
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("secretPersistence")
  public SecretPersistence localTestingSecretPersistence(@Named("configDatabase") final Database configDatabase) {
    return new LocalTestingSecretPersistence(configDatabase);
  }

  @Singleton
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^google_secret_manager$")
  @Named("secretPersistence")
  public SecretPersistence googleSecretPersistence(@Value("${airbyte.secret.store.gcp.credentials}") final String credentials,
                                                   @Value("${airbyte.secret.store.gcp.project-id}") final String projectId) {
    return GoogleSecretManagerPersistence.getLongLived(projectId, credentials);
  }

  @Singleton
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^vault$")
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("secretPersistence")
  public SecretPersistence vaultSecretPersistence(@Value("${airbyte.secret.store.vault.address}") final String address,
                                                  @Value("${airbyte.secret.store.vault.prefix}") final String prefix,
                                                  @Value("${airbyte.secret.store.vault.token}") final String token) {
    return new VaultSecretPersistence(address, prefix, token);
  }

  @Singleton
  @Requires(property = "airbyte.secret.persistence",
            pattern = "(?i)^aws_secret_manager$")
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("secretPersistence")
  public SecretPersistence awsSecretPersistence(@Value("${airbyte.secret.store.aws.access-key}") final String awsAccessKey,
                                                @Value("${airbyte.secret.store.aws.secret-key}") final String awsSecretKey) {
    return new AWSSecretManagerPersistence(awsAccessKey, awsSecretKey);
  }

  @Singleton
  @Requires(property = "airbyte.acceptance.test.enabled",
            value = "true")
  public SecretsHydrator noOpSecretsHydrator() {
    return new NoOpSecretsHydrator();
  }

  @Singleton
  @Requires(property = "airbyte.acceptance.test.enabled",
            value = "false")
  public SecretsHydrator secretsHydrator(@Named("secretPersistence") final SecretPersistence secretPersistence) {
    return new RealSecretsHydrator(secretPersistence);
  }

}
