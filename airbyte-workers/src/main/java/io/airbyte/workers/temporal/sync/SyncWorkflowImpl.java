/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.api.enums.v1.TimeoutType;
import io.temporal.failure.TimeoutFailure;
import io.temporal.workflow.Workflow;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SyncWorkflowImpl implements SyncWorkflow {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncWorkflowImpl.class);
  private static final String VERSION_LABEL = "sync-workflow";
  private static final int CURRENT_VERSION = 1;
  private static final String DATA_PLANE_A = "DATA_PLANE_A";
  private static final String DATA_PLANE_B = "DATA_PLANE_B";

  private final ReplicationActivity replicationActivity =
      Workflow.newActivityStub(ReplicationActivity.class, ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_A));

  private final ReplicationActivity backupReplicationActivity =
      Workflow.newActivityStub(ReplicationActivity.class, ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_B));

  private final NormalizationActivity normalizationActivity =
      Workflow.newActivityStub(NormalizationActivity.class, ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_A));

  private final NormalizationActivity backupNormalizationActivity =
      Workflow.newActivityStub(NormalizationActivity.class, ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_B));

  private final DbtTransformationActivity dbtTransformationActivity =
      Workflow.newActivityStub(DbtTransformationActivity.class,
          ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_A));

  private final DbtTransformationActivity backupDbtTransformationActivity =
      Workflow.newActivityStub(DbtTransformationActivity.class,
          ActivityConfiguration.onTaskQueue(ActivityConfiguration.LONG_RUN_OPTIONS, DATA_PLANE_B));

  private final PersistStateActivity persistActivity =
      Workflow.newActivityStub(PersistStateActivity.class,
          ActivityConfiguration.onTaskQueue(ActivityConfiguration.SHORT_ACTIVITY_OPTIONS, DATA_PLANE_A));

  private final PersistStateActivity backupPersistActivity =
      Workflow.newActivityStub(PersistStateActivity.class,
          ActivityConfiguration.onTaskQueue(ActivityConfiguration.SHORT_ACTIVITY_OPTIONS, DATA_PLANE_B));

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    StandardSyncOutput syncOutput = null;
    try {
      syncOutput = replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);
    } catch (Exception e) {
      LOGGER.error("Caught replication exception");
      if (isScheduleToStartTimeout(e)) {
        LOGGER.warn("Re-routing replication activity to backup");
        syncOutput = backupReplicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);
      }
    }

    final int version = Workflow.getVersion(VERSION_LABEL, Workflow.DEFAULT_VERSION, CURRENT_VERSION);

    if (version > Workflow.DEFAULT_VERSION) {
      // the state is persisted immediately after the replication succeeded, because the
      // state is a checkpoint of the raw data that has been copied to the destination;
      // normalization & dbt does not depend on it
      try {
        persistActivity.persist(connectionId, syncOutput);
      } catch (Exception e) {
        LOGGER.error("Caught persist exception");
        if (isScheduleToStartTimeout(e)) {
          LOGGER.warn("Re-routing persist activity to backup");
          backupPersistActivity.persist(connectionId, syncOutput);
        }
      }
    }

    if (syncInput.getOperationSequence() != null && !syncInput.getOperationSequence().isEmpty()) {
      for (final StandardSyncOperation standardSyncOperation : syncInput.getOperationSequence()) {
        if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
          final NormalizationInput normalizationInput = new NormalizationInput()
              .withDestinationConfiguration(syncInput.getDestinationConfiguration())
              .withCatalog(syncOutput.getOutputCatalog())
              .withResourceRequirements(syncInput.getDestinationResourceRequirements());

          NormalizationSummary normalizationSummary = null;
          try {
            normalizationSummary = normalizationActivity.normalize(jobRunConfig, destinationLauncherConfig, normalizationInput);
          } catch (Exception e) {
            LOGGER.error("Caught normalization exception");
            if (isScheduleToStartTimeout(e)) {
              LOGGER.warn("Re-routing normalization activity to backup");
              normalizationSummary = backupNormalizationActivity.normalize(jobRunConfig, destinationLauncherConfig, normalizationInput);
            }
          }
          syncOutput = syncOutput.withNormalizationSummary(normalizationSummary);

        } else if (standardSyncOperation.getOperatorType() == OperatorType.DBT) {
          final OperatorDbtInput operatorDbtInput = new OperatorDbtInput()
              .withDestinationConfiguration(syncInput.getDestinationConfiguration())
              .withOperatorDbt(standardSyncOperation.getOperatorDbt());

          try {
            dbtTransformationActivity.run(jobRunConfig, destinationLauncherConfig, syncInput.getResourceRequirements(), operatorDbtInput);
          } catch (Exception e) {
            LOGGER.error("Caught dbt exception");
            if (isScheduleToStartTimeout(e)) {
              LOGGER.warn("Re-routing dbt activity to backup");
              backupDbtTransformationActivity.run(jobRunConfig, destinationLauncherConfig, syncInput.getResourceRequirements(), operatorDbtInput);
            }
          }

        } else {
          final String message = String.format("Unsupported operation type: %s", standardSyncOperation.getOperatorType());
          LOGGER.error(message);
          throw new IllegalArgumentException(message);
        }
      }
    }

    return syncOutput;
  }

  private boolean isScheduleToStartTimeout(final Exception e) {
    TimeoutFailure timeoutFailure = null;
    Throwable cause = e;
    int depth = 0;
    while (timeoutFailure == null && depth < 5) {
      if (cause instanceof TimeoutFailure) {
        timeoutFailure = (TimeoutFailure) cause;
      } else {
        depth++;
        cause = cause.getCause();
      }
    }
    if (timeoutFailure == null) {
      LOGGER.warn("caught an exception but didn't find TimeoutException");
      return false;
    } else {
      LOGGER.warn("found timeoutFailure of type {}", timeoutFailure.getTimeoutType());
      return timeoutFailure.getTimeoutType().equals(TimeoutType.TIMEOUT_TYPE_SCHEDULE_TO_START);
    }
  }

}
