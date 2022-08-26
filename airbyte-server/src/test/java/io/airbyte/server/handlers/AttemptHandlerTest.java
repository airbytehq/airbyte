/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doThrow;

import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

class AttemptHandlerTest {

  JobPersistence jobPersistence;
  AttemptHandler handler;

  private static final long JOB_ID = 10002L;
  private static final int ATTEMPT_NUMBER = 1;

  @BeforeEach
  public void init() {
    jobPersistence = Mockito.mock(JobPersistence.class);
    handler = new AttemptHandler(jobPersistence);
  }

  @Test
  void testInternalWorkerHandlerSetsTemporalWorkflowId() throws Exception {
    String workflowId = UUID.randomUUID().toString();

    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);

    SetWorkflowInAttemptRequestBody requestBody =
        new SetWorkflowInAttemptRequestBody().attemptNumber(ATTEMPT_NUMBER).jobId(JOB_ID).workflowId(workflowId);

    assertTrue(handler.setWorkflowInAttempt(requestBody).getSucceeded());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowId(jobIdCapture.capture(), attemptNumberCapture.capture(), workflowIdCapture.capture());

    assertEquals(ATTEMPT_NUMBER, attemptNumberCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
  }

  @Test
  void testInternalWorkerHandlerSetsTemporalWorkflowIdThrows() throws Exception {
    String workflowId = UUID.randomUUID().toString();

    doThrow(IOException.class).when(jobPersistence).setAttemptTemporalWorkflowId(anyLong(), anyInt(),
        any());

    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);

    SetWorkflowInAttemptRequestBody requestBody =
        new SetWorkflowInAttemptRequestBody().attemptNumber(ATTEMPT_NUMBER).jobId(JOB_ID).workflowId(workflowId);

    assertFalse(handler.setWorkflowInAttempt(requestBody).getSucceeded());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowId(jobIdCapture.capture(), attemptNumberCapture.capture(), workflowIdCapture.capture());

    assertEquals(ATTEMPT_NUMBER, attemptNumberCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
  }

}
