/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SyncWorkflowImpl implements SyncWorkflow {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncWorkflowImpl.class);
  private static final String VERSION_LABEL = "sync-workflow";
  private static final int CURRENT_VERSION = 2;
  private static final int PREV_VERSION = 1;

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    final int version = Workflow.getVersion(VERSION_LABEL, Workflow.DEFAULT_VERSION, CURRENT_VERSION);

    final ReplicationActivity replicationActivity;
    final NormalizationActivity normalizationActivity;
    final DbtTransformationActivity dbtTransformationActivity;
    final PersistStateActivity persistActivity;

    /**
     * The current version calls a new activity to determine which Task Queue to use for other
     * activities. The previous version doesn't call this new activity, and instead lets each activity
     * inherit the workflow's Task Queue.
     */
    if (version > PREV_VERSION) {
      final RouteToTaskQueueActivity routeToTaskQueueActivity =
          Workflow.newActivityStub(RouteToTaskQueueActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);

      final String dataPlaneTaskQueue = routeToTaskQueueActivity.routeToTaskQueue(connectionId);

      replicationActivity =
          Workflow.newActivityStub(ReplicationActivity.class, setTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, dataPlaneTaskQueue));
      persistActivity =
          Workflow.newActivityStub(PersistStateActivity.class, setTaskQueue(ActivityConfiguration.SHORT_ACTIVITY_OPTIONS, dataPlaneTaskQueue));
      normalizationActivity =
          Workflow.newActivityStub(NormalizationActivity.class, setTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, dataPlaneTaskQueue));
      dbtTransformationActivity =
          Workflow.newActivityStub(DbtTransformationActivity.class, setTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, dataPlaneTaskQueue));
    } else {
      replicationActivity = Workflow.newActivityStub(ReplicationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
      normalizationActivity = Workflow.newActivityStub(NormalizationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
      dbtTransformationActivity = Workflow.newActivityStub(DbtTransformationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
      persistActivity = Workflow.newActivityStub(PersistStateActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);
    }

    StandardSyncOutput syncOutput = replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

    if (version > Workflow.DEFAULT_VERSION) {
      // the state is persisted immediately after the replication succeeded, because the
      // state is a checkpoint of the raw data that has been copied to the destination;
      // normalization & dbt does not depend on it
      final ConfiguredAirbyteCatalog configuredCatalog = syncInput.getCatalog();
      persistActivity.persist(connectionId, syncOutput, configuredCatalog);
    }

    if (syncInput.getOperationSequence() != null && !syncInput.getOperationSequence().isEmpty()) {
      for (final StandardSyncOperation standardSyncOperation : syncInput.getOperationSequence()) {
        if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
          final Configs configs = new EnvConfigs();
          final NormalizationInput normalizationInput = generateNormalizationInput(syncInput, syncOutput, configs);

          final NormalizationSummary normalizationSummary =
              normalizationActivity.normalize(jobRunConfig, destinationLauncherConfig, normalizationInput);
          syncOutput = syncOutput.withNormalizationSummary(normalizationSummary);
        } else if (standardSyncOperation.getOperatorType() == OperatorType.DBT) {
          final OperatorDbtInput operatorDbtInput = new OperatorDbtInput()
              .withDestinationConfiguration(syncInput.getDestinationConfiguration())
              .withOperatorDbt(standardSyncOperation.getOperatorDbt());

          dbtTransformationActivity.run(jobRunConfig, destinationLauncherConfig, syncInput.getResourceRequirements(), operatorDbtInput);
        } else {
          final String message = String.format("Unsupported operation type: %s", standardSyncOperation.getOperatorType());
          LOGGER.error(message);
          throw new IllegalArgumentException(message);
        }
      }
    }

    return syncOutput;
  }

  private NormalizationInput generateNormalizationInput(final StandardSyncInput syncInput,
                                                        final StandardSyncOutput syncOutput,
                                                        final Configs configs) {
    final ResourceRequirements resourceReqs = new ResourceRequirements()
        .withCpuRequest(configs.getNormalizationJobMainContainerCpuRequest())
        .withCpuLimit(configs.getNormalizationJobMainContainerCpuLimit())
        .withMemoryRequest(configs.getNormalizationJobMainContainerMemoryRequest())
        .withMemoryLimit(configs.getNormalizationJobMainContainerMemoryLimit());

    return new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncOutput.getOutputCatalog())
        .withResourceRequirements(resourceReqs);
  }

  private ActivityOptions setTaskQueue(final ActivityOptions activityOptions, final String taskQueue) {
    return ActivityOptions.newBuilder(activityOptions).setTaskQueue(taskQueue).build();
  }

}
