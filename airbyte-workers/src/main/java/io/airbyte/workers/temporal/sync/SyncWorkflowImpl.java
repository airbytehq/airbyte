/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.FailureReason;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.workflow.Workflow;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.commons.lang3.exception.ExceptionUtils;

public class SyncWorkflowImpl implements SyncWorkflow {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncWorkflowImpl.class);
  private static final String VERSION_LABEL = "sync-workflow";
  private static final int CURRENT_VERSION = 1;

  private final CheckConnectionActivity checkActivity =
      Workflow.newActivityStub(CheckConnectionActivity.class, ActivityConfiguration.CHECK_ACTIVITY_OPTIONS);
  private final ReplicationActivity replicationActivity =
      Workflow.newActivityStub(ReplicationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
  private final NormalizationActivity normalizationActivity =
      Workflow.newActivityStub(NormalizationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
  private final DbtTransformationActivity dbtTransformationActivity =
      Workflow.newActivityStub(DbtTransformationActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);
  private final PersistStateActivity persistActivity =
      Workflow.newActivityStub(PersistStateActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    final StandardCheckConnectionInput sourceConfiguration = new StandardCheckConnectionInput()
        .withConnectionConfiguration(syncInput.getSourceConfiguration());
    final StandardCheckConnectionInput destinationConfiguration =
        new StandardCheckConnectionInput().withConnectionConfiguration(syncInput.getDestinationConfiguration());

    final StandardCheckConnectionOutput sourceCheckResponse = checkActivity.check(jobRunConfig, sourceLauncherConfig, sourceConfiguration);
    if (sourceCheckResponse.getStatus() == Status.FAILED) {
      final Exception ex = new IllegalArgumentException(sourceCheckResponse.toString());
      final FailureReason checkFailureReason = FailureHelper.checkFailure(ex, Long.valueOf(jobRunConfig.getJobId()), Math.toIntExact(jobRunConfig.getAttemptId()), FailureReason.FailureOrigin.SOURCE);
      return new StandardSyncOutput().withFailures(List.of(checkFailureReason));
    }

    final StandardCheckConnectionOutput destinationCheckResponse = checkActivity.check(jobRunConfig, destinationLauncherConfig, destinationConfiguration);
    if (destinationCheckResponse.getStatus() == Status.FAILED) {
      final Exception ex = new IllegalArgumentException(destinationCheckResponse.toString());
      final FailureReason checkFailureReason = FailureHelper.checkFailure(ex, Long.valueOf(jobRunConfig.getJobId()), Math.toIntExact(jobRunConfig.getAttemptId()), FailureReason.FailureOrigin.DESTINATION);
      return new StandardSyncOutput().withFailures(List.of(checkFailureReason));
    }

    StandardSyncOutput syncOutput = replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

    final int version = Workflow.getVersion(VERSION_LABEL, Workflow.DEFAULT_VERSION, CURRENT_VERSION);

    if (version > Workflow.DEFAULT_VERSION) {
      // the state is persisted immediately after the replication succeeded, because the
      // state is a checkpoint of the raw data that has been copied to the destination;
      // normalization & dbt does not depend on it
      persistActivity.persist(connectionId, syncOutput);
    }

    if (syncInput.getOperationSequence() != null && !syncInput.getOperationSequence().isEmpty()) {
      for (final StandardSyncOperation standardSyncOperation : syncInput.getOperationSequence()) {
        if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
          final NormalizationInput normalizationInput = new NormalizationInput()
              .withDestinationConfiguration(syncInput.getDestinationConfiguration())
              .withCatalog(syncOutput.getOutputCatalog())
              .withResourceRequirements(syncInput.getDestinationResourceRequirements());

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
}
