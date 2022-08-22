/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

/**
 * For testing only.
 */
@Slf4j
public class NoOpOrchestrator implements JobOrchestrator<String> {

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
