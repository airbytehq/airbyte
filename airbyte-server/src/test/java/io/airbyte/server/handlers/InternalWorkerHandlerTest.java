/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;

import io.airbyte.api.model.generated.SetTemporalWorkflowInAttemptRequestBody;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.UUID;
import org.junit.Test;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

public class InternalWorkerHandlerTest {

  JobPersistence jobPersistence;
  InternalWorkerHandler handler;

  private static final long JOB_ID = 10002L;
  private static final int ATTEMPT_ID = 1;

  @BeforeEach
  public void init() {
    jobPersistence = Mockito.mock(JobPersistence.class);
    handler = new InternalWorkerHandler(jobPersistence);
  }

  @Test
  void testInternalWorkerHandlerSetsTemporalWorkflowId() throws Exception {
    UUID workflowId = UUID.randomUUID();

    doNothing().when(jobPersistence).setAttemptTemporalWorkflowId(any(), any(), any());

    final ArgumentCaptor<Integer> attemptIdCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);

    SetTemporalWorkflowInAttemptRequestBody requestBody =
        new SetTemporalWorkflowInAttemptRequestBody().attemptId(ATTEMPT_ID).jobId(JOB_ID).temporalWorkflowId(workflowId);

    assertTrue(handler.setTemporalWorkflowInAttempt(requestBody).getDone());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowId(jobIdCapture.capture(), attemptIdCapture.capture(), workflowIdCapture.capture());

    assertEquals(ATTEMPT_ID, attemptIdCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
  }

  @Test
  void testInternalWorkerHandlerSetsTemporalWorkflowIdThrows() throws Exception {
    UUID workflowId = UUID.randomUUID();

    doThrow(IOException.class).when(jobPersistence).setAttemptTemporalWorkflowId(any(), any(), any());

    final ArgumentCaptor<Integer> attemptIdCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);

    SetTemporalWorkflowInAttemptRequestBody requestBody =
        new SetTemporalWorkflowInAttemptRequestBody().attemptId(ATTEMPT_ID).jobId(JOB_ID).temporalWorkflowId(workflowId);

    assertFalse(handler.setTemporalWorkflowInAttempt(requestBody).getDone());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowId(jobIdCapture.capture(), attemptIdCapture.capture(), workflowIdCapture.capture());

    assertEquals(ATTEMPT_ID, attemptIdCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
  }

}
