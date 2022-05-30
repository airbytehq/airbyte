/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.string.Strings;
import io.airbyte.config.EnvConfigs;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@Tag("log4j2-config")
class KubeLoggingConfigTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeLoggingConfigTest.class);
  // We publish every minute. See log4j2.xml.
  private static final long LOG_PUBLISH_DELAY = 70 * 1000;

  private String logPath;

  @AfterEach
  void cleanUpLogs() {
    if (logPath != null) {
      final EnvConfigs envConfigs = new EnvConfigs();
      LogClientSingleton.getInstance().deleteLogs(envConfigs.getWorkerEnvironment(), envConfigs.getLogConfigs(), logPath);
    }
  }

  /**
   * Because this test tests our env var set up is compatible with our Log4j2 configuration, we are
   * unable to perform injection, and instead rely on env vars set in
   * ./tools/bin/cloud_storage_logging_test.sh.
   *
   * This test will fail if certain env vars aren't set.
   */
  @Test
  void testLoggingConfiguration() throws IOException, InterruptedException {
    final EnvConfigs envConfigs = new EnvConfigs();
    final var randPath = Strings.addRandomSuffix("-", "", 5);
    // This mirrors our Log4j2 set up. See log4j2.xml.
    LogClientSingleton.getInstance().setJobMdc(envConfigs.getWorkerEnvironment(), envConfigs.getLogConfigs(), Path.of(randPath));

    final var toLog = List.of("line 1", "line 2", "line 3");
    for (final String l : toLog) {
      LOGGER.info(l);
    }
    // So we don't publish anything else.
    MDC.clear();

    // Sleep to make sure the logs appear.
    Thread.sleep(LOG_PUBLISH_DELAY);

    logPath = randPath + "/logs.log/";
    // The same env vars that log4j2 uses to determine where to publish to determine how to retrieve the
    // log file.
    final var logs = LogClientSingleton.getInstance().getJobLogFile(envConfigs.getWorkerEnvironment(), envConfigs.getLogConfigs(), Path.of(logPath));
    // Each log line is of the form <time-stamp> <log-level> <log-message>. Further, there might be
    // other log lines from the system running. Join all the lines to simplify assertions.
    final var logsLine = Strings.join(logs, " ");
    for (final String l : toLog) {
      assertTrue(logsLine.contains(l));
    }
  }

}
