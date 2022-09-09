/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.micronaut.scheduling.annotation.Scheduled;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class DefinitionsUpdater {

  public DefinitionsUpdater() {
    log.info("Creating connector definitions updater");
  }

  @Inject
  private ConfigRepository configRepository;

  // TODO allow changing rate via config
  @Scheduled(fixedRate = "30s",
             initialDelay = "1m")
  void updateDefinitions() {
    log.info("Updating definitions...");
    final EnvConfigs envConfigs = new EnvConfigs(); // TODO dependency inject this

    // TODO don't run if disabled via env
    envConfigs.getRemoteConnectorCatalogUrl().ifPresent(remoteCatalogUrl -> {
      try {
        final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(remoteCatalogUrl);
        log.info("Retrieved remote definitions: {} sources, {} destinations",
            remoteDefinitionsProvider.getSourceDefinitions().size(),
            remoteDefinitionsProvider.getDestinationDefinitions().size());

        try {
          final ApplyDefinitionsHelper applyHelper = new ApplyDefinitionsHelper(configRepository, remoteDefinitionsProvider);
          applyHelper.apply(envConfigs.getDeploymentMode() == DeploymentMode.CLOUD);

          log.info("Done applying remote connector definitions");
        } catch (final Exception e) {
          log.error("Error while applying remote definitions", e);
        }

      } catch (final Exception e) {
        log.error("Error when retrieving remote definitions", e);
      }
    });

  }

}
