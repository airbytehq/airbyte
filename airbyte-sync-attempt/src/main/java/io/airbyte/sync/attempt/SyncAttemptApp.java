/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.sync.attempt;

import io.airbyte.config.*;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.sync.*;
import io.temporal.workflow.Workflow;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Path;
import java.util.UUID;

public class SyncAttemptApp {


  private static final Logger LOGGER = LoggerFactory.getLogger(SyncAttemptApp.class);

  private final ReplicationActivity replicationActivity;
  private final NormalizationActivity normalizationActivity;
  private final DbtTransformationActivity dbtTransformationActivity;
  private final PersistStateActivity persistActivity;


  public SyncAttemptApp(final ProcessFactory processFactory,
                        final SecretsHydrator secretsHydrator,
                        final Path workspaceRoot,
                        final Configs.WorkerEnvironment workerEnvironment,
                        final LogConfigs logConfigs,
                        final String databaseUser,
                        final String databasePassword,
                        final String databaseUrl,
                        final String airbyteVersion,
                        final ConfigRepository configRepository) {
    replicationActivity = new ReplicationActivityImpl(
            processFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            databaseUser,
            databasePassword,
            databaseUrl,
            airbyteVersion);

    normalizationActivity = new NormalizationActivityImpl(
            processFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            databaseUser,
            databasePassword,
            databaseUrl,
            airbyteVersion);

    dbtTransformationActivity = new DbtTransformationActivityImpl(
            processFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            databaseUser,
            databasePassword,
            databaseUrl,
            airbyteVersion);

    persistActivity = new PersistStateActivityImpl(
            workspaceRoot,
            configRepository);
  }

  public void run(JobRunConfig jobRunConfig,
                  IntegrationLauncherConfig sourceLauncherConfig,
                  IntegrationLauncherConfig destinationLauncherConfig,
                  StandardSyncInput syncInput,
                  UUID connectionId) {
    final StandardSyncOutput run = replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

    persistActivity.persist(connectionId, run);

    if (syncInput.getOperationSequence() != null && !syncInput.getOperationSequence().isEmpty()) {
      for (final StandardSyncOperation standardSyncOperation : syncInput.getOperationSequence()) {
        if (standardSyncOperation.getOperatorType() == StandardSyncOperation.OperatorType.NORMALIZATION) {
          final NormalizationInput normalizationInput = new NormalizationInput()
                  .withDestinationConfiguration(syncInput.getDestinationConfiguration())
                  .withCatalog(run.getOutputCatalog())
                  .withResourceRequirements(syncInput.getResourceRequirements());

          normalizationActivity.normalize(jobRunConfig, destinationLauncherConfig, normalizationInput);
        } else if (standardSyncOperation.getOperatorType() == StandardSyncOperation.OperatorType.DBT) {
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
  }

  public static void main(String[] args) {
    System.out.println("hello world");
  }

}
