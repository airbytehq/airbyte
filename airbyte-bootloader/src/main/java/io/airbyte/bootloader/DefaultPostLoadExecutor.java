/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

/**
 * Default implementation of the tasks that should be executed after a successful bootstrapping of
 * the Airbyte environment.
 * <p>
 * <p>
 * This implementation performs the following tasks:
 * <ul>
 * <li>Applies the latest definitions from the provider to the repository</li>
 * <li>If enables, migrates secrets</li>
 * </ul>
 */
@Singleton
@Slf4j
public class DefaultPostLoadExecutor implements PostLoadExecutor {

  private final ConfigRepository configRepository;

  private final Optional<DefinitionsProvider> definitionsProvider;

  private final FeatureFlags featureFlags;

  private final JobPersistence jobPersistence;

  private final SecretMigrator secretMigrator;

  public DefaultPostLoadExecutor(final ConfigRepository configRepository,
                                 final Optional<DefinitionsProvider> definitionsProvider,
                                 final FeatureFlags featureFlags,
                                 final JobPersistence jobPersistence,
                                 final SecretMigrator secretMigrator) {
    this.configRepository = configRepository;
    this.definitionsProvider = definitionsProvider;
    this.featureFlags = featureFlags;
    this.jobPersistence = jobPersistence;
    this.secretMigrator = secretMigrator;
  }

  @Override
  public void execute() throws JsonValidationException, IOException, ConfigNotFoundException {
    final ApplyDefinitionsHelper applyDefinitionsHelper =
        new ApplyDefinitionsHelper(configRepository, this.definitionsProvider.get(), jobPersistence);
    applyDefinitionsHelper.apply();

    if (featureFlags.forceSecretMigration() || !jobPersistence.isSecretMigrated()) {
      if (this.secretMigrator != null) {
        this.secretMigrator.migrateSecrets();
        log.info("Secrets successfully migrated.");
      }
    }
    log.info("Loaded seed data.");
  }

}
