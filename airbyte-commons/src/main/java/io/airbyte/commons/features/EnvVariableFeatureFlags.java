/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class EnvVariableFeatureFlags implements FeatureFlags {

  @Override
  public boolean usesNewScheduler() {
    log.info("New Scheduler: " + Boolean.parseBoolean(System.getenv("NEW_SCHEDULER")));

    return Boolean.parseBoolean(System.getenv("NEW_SCHEDULER"));
  }

  @Override
  public boolean autoDisablesFailingConnections() {
    log.info("Auto Disable Failing Connections: " + Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS")));

    return Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS"));
  }

  @Override
  public boolean exposeSecretsInExport() {
    return Boolean.parseBoolean(System.getenv("EXPOSE_SECRETS_IN_EXPORT"));
  }

  @Override
  public boolean forceSecretMigration() {
    return Boolean.parseBoolean(System.getenv("FORCE_MIGRATE_SECRET_STORE"));
  }

}
