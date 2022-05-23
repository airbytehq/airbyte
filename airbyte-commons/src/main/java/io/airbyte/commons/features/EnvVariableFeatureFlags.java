/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class EnvVariableFeatureFlags implements FeatureFlags {

  @Override
  public boolean usesNewScheduler() {
    // TODO: sweep this method along with the scheduler
    log.info("New Scheduler: true (post-migration)");

    // After migrating all OSS users onto the new temporal scheduler, this should always return true.
    return true;
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
