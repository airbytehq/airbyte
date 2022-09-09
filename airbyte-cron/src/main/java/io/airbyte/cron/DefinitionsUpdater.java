/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.micronaut.context.annotation.Value;
import io.micronaut.scheduling.annotation.Scheduled;
import java.net.URI;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class DefinitionsUpdater {

  @Inject
  private ConfigRepository configRepository;

  @Value("${airbyte.cron.update-definitions.enabled}")
  private boolean shouldUpdateDefinitions;

  private final URI remoteCatalogUrl;
  private final DeploymentMode deploymentMode;

  public DefinitionsUpdater() {
    log.info("Creating connector definitions updater");

    final EnvConfigs envConfigs = new EnvConfigs();
    remoteCatalogUrl = envConfigs.getRemoteConnectorCatalogUrl().orElse(null);
    deploymentMode = envConfigs.getDeploymentMode();
  }

  @Scheduled(fixedRate = "30s",
             initialDelay = "1m")
  void updateDefinitions() {
    if (!shouldUpdateDefinitions)
      return;

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
