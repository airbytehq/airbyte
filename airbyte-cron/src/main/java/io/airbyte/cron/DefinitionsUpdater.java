/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.scheduling.annotation.Scheduled;
import java.io.IOException;
import java.util.List;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

// 1 - what do we need to instantiate a config repo / connect to the database
// 2 - how does this injection thing work, and how does it need to be configured
// 3 - success

@Singleton
@Slf4j
public class DefinitionsUpdater {

  private static final String DRIVER_CLASS_NAME = DatabaseDriver.POSTGRESQL.getDriverClassName();

  public DefinitionsUpdater() {
    log.info("Creating connector definitions updater");
  }

  @Inject
  private ConfigRepository configRepository;

  @Scheduled(fixedRate = "15s")
  void updateDefinitions() throws JsonValidationException, IOException {
//    try {
      final List<StandardSourceDefinition> defs = configRepository.listStandardSourceDefinitions(false);
      log.info("FOUND {} DEFINITIONS", defs.size());

//    } catch (final Exception e) {
//      log.error(String.valueOf(e));
//    }

  }

}
