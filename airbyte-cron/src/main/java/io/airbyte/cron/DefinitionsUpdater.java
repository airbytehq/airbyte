/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.init.ApplyDefinitionsProvider;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.scheduling.annotation.Scheduled;
import java.io.IOException;
import java.util.List;
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

  @Inject
  private ConfigPersistence configPersistence;

  @Scheduled(fixedRate = "15s")
  void updateDefinitions() throws JsonValidationException, IOException {
    final EnvConfigs envConfigs = new EnvConfigs(); // TODO dependency inject this

    final List<StandardSourceDefinition> defs = configRepository.listStandardSourceDefinitions(false);
    log.info("FOUND {} DEFINITIONS", defs.size());

    // TODO don't run if disabled via env
    envConfigs.getRemoteConnectorCatalogUrl().ifPresent(remoteCatalogUrl -> {
      try {
        final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(remoteCatalogUrl);
        // apply the thing
        final ApplyDefinitionsProvider applyHelper = new ApplyDefinitionsProvider(configRepository, remoteDefinitionsProvider);
        applyHelper.apply(envConfigs.getDeploymentMode() == DeploymentMode.CLOUD);
      } catch (final Exception e) {
        log.error("Error when retrieving remote definitions");
        e.printStackTrace();
      }
    });

  }

}
