/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import io.airbyte.commons.io.LineGobbler;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JavaProcessRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(JavaProcessRunner.class);

  public static void runProcess(final String path, final Runtime run, final String... commands) throws IOException, InterruptedException {
    LOGGER.info("Running process: " + Arrays.asList(commands));
    final Process pr = path.equals(System.getProperty("user.dir")) ? run.exec(commands) : run.exec(commands, null, new File(path));
    LineGobbler.gobble(pr.getErrorStream(), LOGGER::error);
    LineGobbler.gobble(pr.getInputStream(), LOGGER::info);
    if (!pr.waitFor(10, TimeUnit.MINUTES)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + Arrays.toString(commands));
    }
  }

}
