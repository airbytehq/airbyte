/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import static io.airbyte.cron.MicronautCronRunner.SCHEDULED_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.micronaut.context.annotation.Value;
import io.micronaut.scheduling.annotation.Scheduled;
import jakarta.inject.Singleton;
import java.net.URI;
import lombok.extern.slf4j.Slf4j;

/**
 * DefinitionsUpdater
 *
 * Automatically updates connector definitions from a remote catalog at an interval (30s). This can
 * be enabled by setting a REMOTE_CATALOG_URL and UPDATE_DEFINITIONS_CRON_ENABLED=true.
 */
@Singleton
@Slf4j
public class DefinitionsUpdater {

  private final ConfigRepository configRepository;

  private final boolean shouldUpdateDefinitions;

  private final URI remoteCatalogUrl;
  private final DeploymentMode deploymentMode;

  public DefinitionsUpdater(final ConfigRepository configRepository,
                            final DeploymentMode deploymentMode,
                            @Value("${airbyte.remote-connector-catalog-url}") final String remoteCatalogUrl,
                            @Value("${airbyte.cron.update-definitions.enabled}") final boolean shouldUpdateDefinitions) {
    log.info("Creating connector definitions updater");

    this.configRepository = configRepository;
    this.deploymentMode = deploymentMode;
    this.remoteCatalogUrl = remoteCatalogUrl != null ? URI.create(remoteCatalogUrl) : null;
    this.shouldUpdateDefinitions = shouldUpdateDefinitions;
  }

  @Trace(operationName = SCHEDULED_TRACE_OPERATION_NAME)
  @Scheduled(fixedRate = "30s",
             initialDelay = "1m")
  void updateDefinitions() {
    if (!shouldUpdateDefinitions) {
      log.info("Connector definitions update disabled.");
      return;
    }

    if (remoteCatalogUrl == null) {
      log.warn("Tried to update definitions, but the remote catalog url is not set");
      return;
    }

    log.info("Updating definitions...");

    try {
      final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(remoteCatalogUrl);
      log.info("Retrieved remote definitions: {} sources, {} destinations",
          remoteDefinitionsProvider.getSourceDefinitions().size(),
          remoteDefinitionsProvider.getDestinationDefinitions().size());

      try {
        final ApplyDefinitionsHelper applyHelper = new ApplyDefinitionsHelper(configRepository, remoteDefinitionsProvider);
        applyHelper.apply(deploymentMode == DeploymentMode.CLOUD);

        log.info("Done applying remote connector definitions");
      } catch (final Exception e) {
        log.error("Error while applying remote definitions", e);
      }

    } catch (final Exception e) {
      log.error("Error when retrieving remote definitions", e);
    }

  }

}
