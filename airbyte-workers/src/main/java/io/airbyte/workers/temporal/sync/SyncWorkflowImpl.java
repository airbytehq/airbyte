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
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import io.temporal.workflow.Workflow;
import java.util.UUID;
import javax.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class SyncWorkflowImpl implements SyncWorkflow {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncWorkflowImpl.class);
  private static final String VERSION_LABEL = "sync-workflow";
  private static final int CURRENT_VERSION = 2;

  @TemporalActivityStub(activityOptionsBeanName = "longRunActivityOptions",
                        activityGeneratorBeanName = "multiCloudTemporalActivityStubGeneratorFunction",
                        workflowVersionChangeId = "sync-workflow")
  private ReplicationActivity replicationActivity;
  @TemporalActivityStub(activityOptionsBeanName = "longRunActivityOptions",
                        activityGeneratorBeanName = "multiCloudTemporalActivityStubGeneratorFunction",
                        workflowVersionChangeId = "sync-workflow")
  private NormalizationActivity normalizationActivity;
  @TemporalActivityStub(activityOptionsBeanName = "longRunActivityOptions",
                        activityGeneratorBeanName = "multiCloudTemporalActivityStubGeneratorFunction",
                        workflowVersionChangeId = "sync-workflow")
  private DbtTransformationActivity dbtTransformationActivity;
  @TemporalActivityStub(activityOptionsBeanName = "shortActivityOptions",
                        activityGeneratorBeanName = "multiCloudTemporalActivityStubGeneratorFunction",
                        workflowVersionChangeId = "sync-workflow")
  private PersistStateActivity persistActivity;

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    final int version = Workflow.getVersion(VERSION_LABEL, Workflow.DEFAULT_VERSION, CURRENT_VERSION);
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
          final NormalizationInput normalizationInput = generateNormalizationInput(syncInput, syncOutput);
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
                                                        final StandardSyncOutput syncOutput) {

    return normalizationActivity.generateNormalizationInput(syncInput, syncOutput);
  }

}
