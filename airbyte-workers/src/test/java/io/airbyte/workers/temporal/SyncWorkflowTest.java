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

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.temporal.SyncWorkflow.NormalizationActivity;
import io.airbyte.workers.temporal.SyncWorkflow.NormalizationActivityImpl;
import io.airbyte.workers.temporal.SyncWorkflow.ReplicationActivity;
import io.airbyte.workers.temporal.SyncWorkflow.ReplicationActivityImpl;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowFailedException;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// based of example in temporal samples:
// https://github.com/temporalio/samples-java/blob/master/src/test/java/io/temporal/samples/hello/HelloActivityTest.java
class SyncWorkflowTest {

  // TEMPORAL
  private static final String TASK_QUEUE = "a";

  private TestWorkflowEnvironment testEnv;
  private Worker worker;
  private WorkflowClient client;
  private ReplicationActivityImpl replicationActivity;
  private NormalizationActivityImpl normalizationActivity;

  // AIRBYTE CONFIGURATION
  private static final long JOB_ID = 11L;
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID);
  private static final String IMAGE_NAME1 = "hms invincible";
  private static final String IMAGE_NAME2 = "hms defiant";
  private static final IntegrationLauncherConfig SOURCE_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);
  private static final IntegrationLauncherConfig DESTINATION_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME2);

  private StandardSyncInput syncInput;
  private NormalizationInput normalizationInput;

  private StandardSyncOutput replicationSuccessOutput;

  @BeforeEach
  public void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();
    worker = testEnv.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(SyncWorkflow.WorkflowImpl.class);

    client = testEnv.getWorkflowClient();

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    syncInput = syncPair.getValue();
    replicationSuccessOutput = new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog());

    normalizationInput = new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncInput.getCatalog());

    replicationActivity = mock(ReplicationActivityImpl.class);
    normalizationActivity = mock(NormalizationActivityImpl.class);
  }

  // bundle up all of the temporal worker setup / execution into one method.
  private StandardSyncOutput execute() {
    worker.registerActivitiesImplementations(replicationActivity, normalizationActivity);
    testEnv.start();
    final SyncWorkflow workflow = client.newWorkflowStub(SyncWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).build());

    return workflow.run(JOB_RUN_CONFIG, SOURCE_LAUNCHER_CONFIG, DESTINATION_LAUNCHER_CONFIG, syncInput);
  }

  @Test
  void testSuccess() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    final StandardSyncOutput actualOutput = execute();
    assertEquals(replicationSuccessOutput, actualOutput);

    verifyReplication(replicationActivity, syncInput);
    verifyNormalize(normalizationActivity, normalizationInput);
  }

  @Test
  void testReplicationFailure() {
    doThrow(new IllegalArgumentException("induced exception")).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput);
    verifyNoInteractions(normalizationActivity);
  }

  @Test
  void testNormalizationFailure() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    doThrow(new IllegalArgumentException("induced exception")).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput);
    verifyNormalize(normalizationActivity, normalizationInput);
  }

  private static void verifyReplication(ReplicationActivity replicationActivity, StandardSyncInput syncInput) {
    verify(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);
  }

  private static void verifyNormalize(NormalizationActivity normalizationActivity, NormalizationInput normalizationInput) {
    verify(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

}
