/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.config.init.PostLoadExecutor;
import io.airbyte.persistence.job.JobPersistence;
import jakarta.inject.Singleton;
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

  private final ApplyDefinitionsHelper applyDefinitionsHelper;
  private final FeatureFlags featureFlags;
  private final JobPersistence jobPersistence;
  private final SecretMigrator secretMigrator;

  public DefaultPostLoadExecutor(final ApplyDefinitionsHelper applyDefinitionsHelper,
                                 final FeatureFlags featureFlags,
                                 final JobPersistence jobPersistence,
                                 final SecretMigrator secretMigrator) {
    this.applyDefinitionsHelper = applyDefinitionsHelper;
    this.featureFlags = featureFlags;
    this.jobPersistence = jobPersistence;
    this.secretMigrator = secretMigrator;
  }

  @Override
  public void execute() throws Exception {
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
