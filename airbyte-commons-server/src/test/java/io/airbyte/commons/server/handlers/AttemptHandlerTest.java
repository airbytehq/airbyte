/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doThrow;

import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.persistence.job.JobPersistence;
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

  private static final String PROCESSING_TASK_QUEUE = "SYNC";

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
    final ArgumentCaptor<String> queueCapture = ArgumentCaptor.forClass(String.class);

    SetWorkflowInAttemptRequestBody requestBody =
        new SetWorkflowInAttemptRequestBody().attemptNumber(ATTEMPT_NUMBER).jobId(JOB_ID).workflowId(workflowId)
            .processingTaskQueue(PROCESSING_TASK_QUEUE);

    assertTrue(handler.setWorkflowInAttempt(requestBody).getSucceeded());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowInfo(jobIdCapture.capture(), attemptNumberCapture.capture(), workflowIdCapture.capture(),
        queueCapture.capture());

    assertEquals(ATTEMPT_NUMBER, attemptNumberCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
    assertEquals(PROCESSING_TASK_QUEUE, queueCapture.getValue());
  }

  @Test
  void testInternalWorkerHandlerSetsTemporalWorkflowIdThrows() throws Exception {
    String workflowId = UUID.randomUUID().toString();

    doThrow(IOException.class).when(jobPersistence).setAttemptTemporalWorkflowInfo(anyLong(), anyInt(),
        any(), any());

    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);
    final ArgumentCaptor<String> queueCapture = ArgumentCaptor.forClass(String.class);

    SetWorkflowInAttemptRequestBody requestBody =
        new SetWorkflowInAttemptRequestBody().attemptNumber(ATTEMPT_NUMBER).jobId(JOB_ID).workflowId(workflowId)
            .processingTaskQueue(PROCESSING_TASK_QUEUE);

    assertFalse(handler.setWorkflowInAttempt(requestBody).getSucceeded());

    Mockito.verify(jobPersistence).setAttemptTemporalWorkflowInfo(jobIdCapture.capture(), attemptNumberCapture.capture(), workflowIdCapture.capture(),
        queueCapture.capture());

    assertEquals(ATTEMPT_NUMBER, attemptNumberCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(workflowId, workflowIdCapture.getValue());
    assertEquals(PROCESSING_TASK_QUEUE, queueCapture.getValue());
  }

}
