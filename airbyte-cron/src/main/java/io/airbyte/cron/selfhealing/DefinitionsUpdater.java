/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import static io.airbyte.cron.MicronautCronRunner.SCHEDULED_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.micronaut.context.annotation.Requires;
import io.micronaut.scheduling.annotation.Scheduled;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * DefinitionsUpdater
 *
 * Automatically updates connector definitions from a remote catalog at an interval (30s). This can
 * be enabled by setting a REMOTE_CATALOG_URL and UPDATE_DEFINITIONS_CRON_ENABLED=true.
 */
@Singleton
@Slf4j
@Requires(property = "airbyte.cron.update-definitions.enabled",
          value = "true")
public class DefinitionsUpdater {

  private final ApplyDefinitionsHelper applyDefinitionsHelper;
  private final DeploymentMode deploymentMode;

  public DefinitionsUpdater(final ApplyDefinitionsHelper applyDefinitionsHelper,
                            final DeploymentMode deploymentMode) {
    log.info("Creating connector definitions updater");

    this.applyDefinitionsHelper = applyDefinitionsHelper;
    this.deploymentMode = deploymentMode;
  }

  @Trace(operationName = SCHEDULED_TRACE_OPERATION_NAME)
  @Scheduled(fixedRate = "30s",
             initialDelay = "1m")
  void updateDefinitions() {
    log.info("Updating definitions...");

    try {
      try {
        applyDefinitionsHelper.apply(deploymentMode == DeploymentMode.CLOUD);

        log.info("Done applying remote connector definitions");
      } catch (final Exception e) {
        log.error("Error while applying remote definitions", e);
      }

    } catch (final Exception e) {
      log.error("Error when retrieving remote definitions", e);
    }

  }

}
