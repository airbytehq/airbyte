/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.workers.Worker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EchoWorker implements Worker<String, String> {

  private static final Logger LOGGER = LoggerFactory.getLogger(EchoWorker.class);

  public EchoWorker() {}

  @Override
  public String run(final String string, final Path jobRoot) {
    LOGGER.info("Hello World. input: {}, workspace root: {}", string, jobRoot);
    return "echoed";
  }

  @Override
  public void cancel() {
    // no-op
  }

}
