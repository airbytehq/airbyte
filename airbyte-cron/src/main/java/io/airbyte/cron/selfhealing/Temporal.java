/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import io.micronaut.scheduling.annotation.Scheduled;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class Temporal {

  public Temporal() {
    log.info("Creating temporal self-healing");
  }

  @Scheduled(fixedRate = "10s")
  void cleanTemporal() {}

}
