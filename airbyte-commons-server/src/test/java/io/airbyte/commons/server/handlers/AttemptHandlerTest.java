/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doThrow;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.generated.AttemptSyncConfig;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.GlobalState;
import io.airbyte.api.model.generated.SaveAttemptSyncConfigRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.persistence.job.JobPersistence;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

class AttemptHandlerTest {

  JobPersistence jobPersistence;
  AttemptHandler handler;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
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
    final String workflowId = UUID.randomUUID().toString();

    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);
    final ArgumentCaptor<String> queueCapture = ArgumentCaptor.forClass(String.class);

    final SetWorkflowInAttemptRequestBody requestBody =
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
    final String workflowId = UUID.randomUUID().toString();

    doThrow(IOException.class).when(jobPersistence).setAttemptTemporalWorkflowInfo(anyLong(), anyInt(),
        any(), any());

    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<String> workflowIdCapture = ArgumentCaptor.forClass(String.class);
    final ArgumentCaptor<String> queueCapture = ArgumentCaptor.forClass(String.class);

    final SetWorkflowInAttemptRequestBody requestBody =
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

  @Test
  void testInternalHandlerSetsAttemptSyncConfig() throws Exception {
    final ArgumentCaptor<Integer> attemptNumberCapture = ArgumentCaptor.forClass(Integer.class);
    final ArgumentCaptor<Long> jobIdCapture = ArgumentCaptor.forClass(Long.class);
    final ArgumentCaptor<io.airbyte.config.AttemptSyncConfig> attemptSyncConfigCapture =
        ArgumentCaptor.forClass(io.airbyte.config.AttemptSyncConfig.class);

    final JsonNode sourceConfig = Jsons.jsonNode(Map.of("source_key", "source_val"));
    final JsonNode destinationConfig = Jsons.jsonNode(Map.of("destination_key", "destination_val"));
    final ConnectionState state = new ConnectionState()
        .connectionId(CONNECTION_ID)
        .stateType(ConnectionStateType.GLOBAL)
        .streamState(null)
        .globalState(new GlobalState().sharedState(Jsons.jsonNode(Map.of("state_key", "state_val"))));

    final AttemptSyncConfig attemptSyncConfig = new AttemptSyncConfig()
        .destinationConfiguration(destinationConfig)
        .sourceConfiguration(sourceConfig)
        .state(state);

    final SaveAttemptSyncConfigRequestBody requestBody =
        new SaveAttemptSyncConfigRequestBody().attemptNumber(ATTEMPT_NUMBER).jobId(JOB_ID).syncConfig(attemptSyncConfig);

    assertTrue(handler.saveSyncConfig(requestBody).getSucceeded());

    Mockito.verify(jobPersistence).writeAttemptSyncConfig(jobIdCapture.capture(), attemptNumberCapture.capture(), attemptSyncConfigCapture.capture());

    final io.airbyte.config.AttemptSyncConfig expectedAttemptSyncConfig = ApiPojoConverters.attemptSyncConfigToInternal(attemptSyncConfig);

    assertEquals(ATTEMPT_NUMBER, attemptNumberCapture.getValue());
    assertEquals(JOB_ID, jobIdCapture.getValue());
    assertEquals(expectedAttemptSyncConfig, attemptSyncConfigCapture.getValue());
  }

}
