/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
public class KubeLoggingConfigTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeLoggingConfigTest.class);
  // We publish every minute. See log4j2.xml.
  private static final long LOG_PUBLISH_DELAY = 70 * 1000;

  private String logPath;

  @AfterEach
  public void cleanUpLogs() {
    if (logPath != null) {
      try {
        LogClientSingleton.deleteLogs(new EnvConfigs(), logPath);
      } catch (Exception e) {
        // Ignore Minio delete error.
      }
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
  public void testLoggingConfiguration() throws IOException, InterruptedException {
    var randPath = Strings.addRandomSuffix("-", "", 5);
    // This mirrors our Log4j2 set up. See log4j2.xml.
    LogClientSingleton.setJobMdc(Path.of(randPath));

    var toLog = List.of("line 1", "line 2", "line 3");
    for (String l : toLog) {
      LOGGER.info(l);
    }
    // So we don't publish anything else.
    MDC.clear();

    // Sleep to make sure the logs appear.
    Thread.sleep(LOG_PUBLISH_DELAY);

    logPath = randPath + "/logs.log/";
    // The same env vars that log4j2 uses to determine where to publish to determine how to retrieve the
    // log file.
    var logs = LogClientSingleton.getJobLogFile(new EnvConfigs(), Path.of(logPath));
    // Each log line is of the form <time-stamp> <log-level> <log-message>. Further, there might be
    // other log lines from the system running. Join all the lines to simplify assertions.
    var logsLine = Strings.join(logs, " ");
    for (String l : toLog) {
      assertTrue(logsLine.contains(l));
    }
  }

}
