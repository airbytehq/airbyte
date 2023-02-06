/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.OperatorWebhook;
import io.airbyte.config.OperatorWebhookInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.SyncStats;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivityImpl;
import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityOptions;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import io.temporal.api.workflowservice.v1.WorkflowServiceGrpc.WorkflowServiceBlockingStub;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowFailedException;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.RetryOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

@SuppressWarnings({"PMD.UnusedPrivateField", "PMD.UnusedPrivateMethod"})
class SyncWorkflowTest {

  private static final String WEBHOOK_URL = "http://example.com";
  private static final String WEBHOOK_BODY = "webhook-body";
  private static final UUID WEBHOOK_CONFIG_ID = UUID.randomUUID();

  // TEMPORAL

  private TestWorkflowEnvironment testEnv;
  private Worker syncWorker;
  private WorkflowClient client;
  private ReplicationActivityImpl replicationActivity;
  private NormalizationActivityImpl normalizationActivity;
  private DbtTransformationActivityImpl dbtTransformationActivity;
  private PersistStateActivityImpl persistStateActivity;
  private NormalizationSummaryCheckActivityImpl normalizationSummaryCheckActivity;
  private WebhookOperationActivityImpl webhookOperationActivity;
  private RefreshSchemaActivityImpl refreshSchemaActivity;
  private ConfigFetchActivityImpl configFetchActivity;

  // AIRBYTE CONFIGURATION
  private static final long JOB_ID = 11L;
  private static final int ATTEMPT_ID = 21;
  private static final UUID SOURCE_ID = UUID.randomUUID();
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

  private static final String SYNC_QUEUE = "SYNC";

  private StandardSync sync;
  private StandardSyncInput syncInput;
  private NormalizationInput normalizationInput;
  private OperatorDbtInput operatorDbtInput;
  private StandardSyncOutput replicationSuccessOutput;
  private StandardSyncOutput replicationFailOutput;
  private StandardSyncSummary standardSyncSummary;
  private StandardSyncSummary failedSyncSummary;
  private SyncStats syncStats;
  private NormalizationSummary normalizationSummary;
  private ActivityOptions longActivityOptions;
  private ActivityOptions shortActivityOptions;

  private ActivityOptions discoveryActivityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  @BeforeEach
  void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();
    syncWorker = testEnv.newWorker(SYNC_QUEUE);
    client = testEnv.getWorkflowClient();

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    sync = syncPair.getKey();
    syncInput = syncPair.getValue();

    syncStats = new SyncStats().withRecordsCommitted(10L);
    standardSyncSummary = new StandardSyncSummary().withTotalStats(syncStats);
    failedSyncSummary = new StandardSyncSummary().withStatus(ReplicationStatus.FAILED).withTotalStats(new SyncStats().withRecordsEmitted(0L));
    replicationSuccessOutput = new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog()).withStandardSyncSummary(standardSyncSummary);
    replicationFailOutput = new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog()).withStandardSyncSummary(failedSyncSummary);

    normalizationSummary = new NormalizationSummary();

    normalizationInput = new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncInput.getCatalog())
        .withResourceRequirements(new ResourceRequirements());

    operatorDbtInput = new OperatorDbtInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withOperatorDbt(syncInput.getOperationSequence().get(1).getOperatorDbt());

    replicationActivity = mock(ReplicationActivityImpl.class);
    normalizationActivity = mock(NormalizationActivityImpl.class);
    dbtTransformationActivity = mock(DbtTransformationActivityImpl.class);
    persistStateActivity = mock(PersistStateActivityImpl.class);
    normalizationSummaryCheckActivity = mock(NormalizationSummaryCheckActivityImpl.class);
    webhookOperationActivity = mock(WebhookOperationActivityImpl.class);
    refreshSchemaActivity = mock(RefreshSchemaActivityImpl.class);
    configFetchActivity = mock(ConfigFetchActivityImpl.class);

    when(normalizationActivity.generateNormalizationInput(any(), any())).thenReturn(normalizationInput);
    when(normalizationSummaryCheckActivity.shouldRunNormalization(any(), any(), any())).thenReturn(true);

    when(configFetchActivity.getSourceId(sync.getConnectionId())).thenReturn(Optional.of(SOURCE_ID));
    when(refreshSchemaActivity.shouldRefreshSchema(SOURCE_ID)).thenReturn(true);
    when(configFetchActivity.getStatus(sync.getConnectionId())).thenReturn(Optional.of(ConnectionStatus.ACTIVE));

    longActivityOptions = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofDays(3))
        .setStartToCloseTimeout(Duration.ofDays(3))
        .setScheduleToStartTimeout(Duration.ofDays(3))
        .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .setHeartbeatTimeout(TemporalUtils.HEARTBEAT_TIMEOUT)
        .build();
    shortActivityOptions = ActivityOptions.newBuilder()
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())
        .build();
    discoveryActivityOptions = ActivityOptions.newBuilder()
        .setStartToCloseTimeout(Duration.ofSeconds(360))
        .build();

    final BeanIdentifier longActivitiesBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration longActivityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(longActivitiesBeanIdentifier.getName()).thenReturn("longRunActivityOptions");
    when(longActivityOptionsBeanRegistration.getIdentifier()).thenReturn(longActivitiesBeanIdentifier);
    when(longActivityOptionsBeanRegistration.getBean()).thenReturn(longActivityOptions);
    final BeanIdentifier shortActivitiesBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration shortActivityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(shortActivitiesBeanIdentifier.getName()).thenReturn("shortActivityOptions");
    when(shortActivityOptionsBeanRegistration.getIdentifier()).thenReturn(shortActivitiesBeanIdentifier);
    when(shortActivityOptionsBeanRegistration.getBean()).thenReturn(shortActivityOptions);
    final BeanIdentifier discoveryActivityBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration discoveryActivityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(discoveryActivityBeanIdentifier.getName()).thenReturn("discoveryActivityOptions");
    when(discoveryActivityOptionsBeanRegistration.getIdentifier()).thenReturn(discoveryActivityBeanIdentifier);
    when(discoveryActivityOptionsBeanRegistration.getBean()).thenReturn(discoveryActivityOptions);
    temporalProxyHelper = new TemporalProxyHelper(
        List.of(longActivityOptionsBeanRegistration, shortActivityOptionsBeanRegistration, discoveryActivityOptionsBeanRegistration));

    syncWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(SyncWorkflowImpl.class));
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

  // bundle up all the temporal worker setup / execution into one method.
  private StandardSyncOutput execute() {
    syncWorker.registerActivitiesImplementations(replicationActivity, normalizationActivity, dbtTransformationActivity,
        persistStateActivity, normalizationSummaryCheckActivity, webhookOperationActivity, refreshSchemaActivity, configFetchActivity);
    testEnv.start();
    final SyncWorkflow workflow =
        client.newWorkflowStub(SyncWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(SYNC_QUEUE).build());

    return workflow.run(JOB_RUN_CONFIG, SOURCE_LAUNCHER_CONFIG, DESTINATION_LAUNCHER_CONFIG, syncInput, sync.getConnectionId());
  }

  @Test
  void testSuccess() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    doReturn(normalizationSummary).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    final StandardSyncOutput actualOutput = execute();

    verifyReplication(replicationActivity, syncInput);
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput, syncInput.getCatalog());
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyDbtTransform(dbtTransformationActivity, syncInput.getResourceRequirements(),
        operatorDbtInput);
    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    assertEquals(
        replicationSuccessOutput.withNormalizationSummary(normalizationSummary).getStandardSyncSummary(),
        actualOutput.getStandardSyncSummary());
  }

  @Test
  void testReplicationFailure() {
    doThrow(new IllegalArgumentException("induced exception")).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyNoInteractions(persistStateActivity);
    verifyNoInteractions(normalizationActivity);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  void testReplicationFailedGracefully() {
    doReturn(replicationFailOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    doReturn(normalizationSummary).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    final StandardSyncOutput actualOutput = execute();

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyPersistState(persistStateActivity, sync, replicationFailOutput, syncInput.getCatalog());
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyDbtTransform(dbtTransformationActivity, syncInput.getResourceRequirements(),
        operatorDbtInput);
    assertEquals(
        replicationFailOutput.withNormalizationSummary(normalizationSummary).getStandardSyncSummary(),
        actualOutput.getStandardSyncSummary());
  }

  @Test
  void testNormalizationFailure() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    doThrow(new IllegalArgumentException("induced exception")).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput, syncInput.getCatalog());
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  void testCancelDuringReplication() {
    doAnswer(ignored -> {
      cancelWorkflow();
      return replicationSuccessOutput;
    }).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyNoInteractions(persistStateActivity);
    verifyNoInteractions(normalizationActivity);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  void testCancelDuringNormalization() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    doAnswer(ignored -> {
      cancelWorkflow();
      return replicationSuccessOutput;
    }).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput, syncInput.getCatalog());
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  @Disabled("This behavior has been disabled temporarily (OC Issue #741)")
  void testSkipNormalization() {
    final SyncStats syncStats = new SyncStats().withRecordsCommitted(0L);
    final StandardSyncSummary standardSyncSummary = new StandardSyncSummary().withTotalStats(syncStats);
    final StandardSyncOutput replicationSuccessOutputNoRecordsCommitted =
        new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog()).withStandardSyncSummary(standardSyncSummary);
    when(normalizationSummaryCheckActivity.shouldRunNormalization(any(), any(), any())).thenReturn(false);

    doReturn(replicationSuccessOutputNoRecordsCommitted).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);

    execute();

    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyReplication(replicationActivity, syncInput);
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutputNoRecordsCommitted, syncInput.getCatalog());
    verifyNoInteractions(normalizationActivity);
    verifyDbtTransform(dbtTransformationActivity, syncInput.getResourceRequirements(),
        operatorDbtInput);
  }

  @Test
  void testWebhookOperation() {
    when(replicationActivity.replicate(any(), any(), any(), any(), any())).thenReturn(new StandardSyncOutput());
    final StandardSyncOperation webhookOperation = new StandardSyncOperation()
        .withOperationId(UUID.randomUUID())
        .withOperatorType(OperatorType.WEBHOOK)
        .withOperatorWebhook(new OperatorWebhook()
            .withExecutionUrl(WEBHOOK_URL)
            .withExecutionBody(WEBHOOK_BODY)
            .withWebhookConfigId(WEBHOOK_CONFIG_ID));
    final JsonNode workspaceWebhookConfigs = Jsons.emptyObject();
    syncInput.withOperationSequence(List.of(webhookOperation)).withWebhookOperationConfigs(workspaceWebhookConfigs);
    when(webhookOperationActivity.invokeWebhook(
        new OperatorWebhookInput().withWebhookConfigId(WEBHOOK_CONFIG_ID).withExecutionUrl(WEBHOOK_URL).withExecutionBody(WEBHOOK_BODY)
            .withWorkspaceWebhookConfigs(workspaceWebhookConfigs))).thenReturn(true);
    final StandardSyncOutput actualOutput = execute();
    assertEquals(actualOutput.getWebhookOperationSummary().getSuccesses().get(0), WEBHOOK_CONFIG_ID);
  }

  @Test
  void testSkipReplicationAfterRefreshSchema() {
    when(configFetchActivity.getStatus(any())).thenReturn(Optional.of(ConnectionStatus.INACTIVE));
    final StandardSyncOutput output = execute();
    verifyShouldRefreshSchema(refreshSchemaActivity);
    verifyRefreshSchema(refreshSchemaActivity, sync);
    verifyNoInteractions(replicationActivity);
    verifyNoInteractions(normalizationActivity);
    assertEquals(output.getStandardSyncSummary().getStatus(), ReplicationStatus.CANCELLED);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  private void cancelWorkflow() {
    final WorkflowServiceBlockingStub temporalService = testEnv.getWorkflowService().blockingStub();
    // there should only be one execution running.
    final String workflowId = temporalService.listOpenWorkflowExecutions(null).getExecutionsList().get(0).getExecution().getWorkflowId();

    final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
        .setWorkflowId(workflowId)
        .build();

    final RequestCancelWorkflowExecutionRequest cancelRequest = RequestCancelWorkflowExecutionRequest.newBuilder()
        .setWorkflowExecution(workflowExecution)
        .build();

    testEnv.getWorkflowService().blockingStub().requestCancelWorkflowExecution(cancelRequest);
  }

  private static void verifyReplication(final ReplicationActivity replicationActivity, final StandardSyncInput syncInput) {
    verify(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput, SYNC_QUEUE);
  }

  private static void verifyPersistState(final PersistStateActivity persistStateActivity,
                                         final StandardSync sync,
                                         final StandardSyncOutput syncOutput,
                                         final ConfiguredAirbyteCatalog configuredCatalog) {
    verify(persistStateActivity).persist(
        sync.getConnectionId(),
        syncOutput,
        configuredCatalog);
  }

  private static void verifyNormalize(final NormalizationActivity normalizationActivity, final NormalizationInput normalizationInput) {
    verify(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);
  }

  private static void verifyDbtTransform(final DbtTransformationActivity dbtTransformationActivity,
                                         final ResourceRequirements resourceRequirements,
                                         final OperatorDbtInput operatorDbtInput) {
    verify(dbtTransformationActivity).run(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        resourceRequirements,
        operatorDbtInput);
  }

  private static void verifyShouldRefreshSchema(final RefreshSchemaActivity refreshSchemaActivity) {
    verify(refreshSchemaActivity).shouldRefreshSchema(SOURCE_ID);
  }

  private static void verifyRefreshSchema(final RefreshSchemaActivity refreshSchemaActivity, final StandardSync sync) {
    verify(refreshSchemaActivity).refreshSchema(SOURCE_ID, sync.getConnectionId());
  }

}
