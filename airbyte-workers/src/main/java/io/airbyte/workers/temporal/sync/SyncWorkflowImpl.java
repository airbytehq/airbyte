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
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.workflow.Workflow;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

    StandardCheckConnectionOutput sourceCheckOutput = checkActivity.check(jobRunConfig, sourceLauncherConfig, sourceConfiguration);
    StandardCheckConnectionOutput destinationCheckOutput = checkActivity.check(jobRunConfig, destinationLauncherConfig, destinationConfiguration);

    // if (sourceCheckOutput.getStatus() == Status.FAILED) {
    // ThrowAndLogError("Source check failed");
    // }
    // else if (destinationCheckOutput.getStatus() == Status.FAILED) {
    // ThrowAndLogError("Destination check failed");
    // }

    // boolean source_check_passed = true;
    // boolean destination_check_passed = true;
    // try {
    //// System.out.println("----- SOURCE START");
    // StandardCheckConnectionOutput sourceCheckOutput = checkActivity.check(jobRunConfig,
    // sourceLauncherConfig, sourceConfiguration);
    //// System.out.println("----- SOURCE RESPONSE");
    //// System.out.println(sourceCheckOutput);
    // } catch (ActivityFailure e) {
    // source_check_passed = false;
    // }
    //
    // try {
    //// System.out.println("----- DESTINATION START");
    // StandardCheckConnectionOutput destinationCheckOutput = checkActivity.check(jobRunConfig,
    // destinationLauncherConfig, destinationConfiguration);
    //// System.out.println("----- DESTINATION RESPONSE");
    //// System.out.println(destinationCheckOutput);
    // } catch (ActivityFailure e) {
    // destination_check_passed = false;
    // }

    /*
     * If there is an error with either of the connection CHECKs, return early with a FailureReason
     */
    if (sourceCheckOutput.getStatus() != Status.SUCCEEDED || destinationCheckOutput.getStatus() != Status.SUCCEEDED) {
      StandardSyncOutput failureSyncOutput = new StandardSyncOutput();
      List<FailureReason> failures = new ArrayList<FailureReason>();
      failureSyncOutput.setFailures(failures);
      return failureSyncOutput;
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
          ThrowAndLogError(String.format("Unsupported operation type: %s", standardSyncOperation.getOperatorType()));
        }
      }
    }

    return syncOutput;
  }

  private void ThrowAndLogError(String message) {
    LOGGER.error(message);
    throw new IllegalArgumentException(message);
  }

}
