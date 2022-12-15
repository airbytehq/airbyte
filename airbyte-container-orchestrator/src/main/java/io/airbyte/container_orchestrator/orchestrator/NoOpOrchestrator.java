/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.orchestrator;

import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import java.lang.invoke.MethodHandles;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * For testing only.
 */
public class NoOpOrchestrator implements JobOrchestrator<String> {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  @Override
  public String getOrchestratorName() {
    return AsyncOrchestratorPodProcess.NO_OP;
  }

  @Override
  public Class<String> getInputClass() {
    return String.class;
  }

  @Override
  public Optional<String> runJob() throws Exception {
    log.info("Running no-op job.");
    return Optional.empty();
  }

}
