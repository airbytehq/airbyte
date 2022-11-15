/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.container_orchestrator.orchestrator.JobOrchestrator;
import io.airbyte.workers.process.AsyncKubePodStatus;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ApplicationTest {

  private String application;
  private JobOrchestrator<?> jobOrchestrator;
  private AsyncStateManager asyncStateManager;

  @BeforeEach
  void setup() {
    jobOrchestrator = mock(JobOrchestrator.class);
    asyncStateManager = mock(AsyncStateManager.class);
  }

  @Test
  void testHappyPath() throws Exception {
    final var output = "job-output";
    when(jobOrchestrator.runJob()).thenReturn(Optional.of(output));

    final var app = new Application(application, jobOrchestrator, asyncStateManager);
    final var code = app.run();

    assertEquals(0, code);
    verify(jobOrchestrator).runJob();
    verify(asyncStateManager).write(AsyncKubePodStatus.INITIALIZING);
    verify(asyncStateManager).write(AsyncKubePodStatus.RUNNING);
    verify(asyncStateManager).write(AsyncKubePodStatus.SUCCEEDED, output);
  }

  @Test
  void testJobFailedWritesFailedStatus() throws Exception {
    when(jobOrchestrator.runJob()).thenThrow(new Exception());
    final var app = new Application(application, jobOrchestrator, asyncStateManager);
    final var code = app.run();

    assertEquals(1, code);
    verify(jobOrchestrator).runJob();
    verify(asyncStateManager).write(AsyncKubePodStatus.INITIALIZING);
    verify(asyncStateManager).write(AsyncKubePodStatus.RUNNING);
    verify(asyncStateManager).write(AsyncKubePodStatus.FAILED);
  }

}
