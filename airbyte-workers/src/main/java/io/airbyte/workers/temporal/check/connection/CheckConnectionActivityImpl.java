/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;

public class CheckConnectionActivityImpl implements CheckConnectionActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final JobPersistence jobPersistence;
  private final String airbyteVersion;

  public CheckConnectionActivityImpl(final WorkerConfigs workerConfigs,
                                     final ProcessFactory processFactory,
                                     final SecretsHydrator secretsHydrator,
                                     final Path workspaceRoot,
                                     final WorkerEnvironment workerEnvironment,
                                     final LogConfigs logConfigs,
                                     final JobPersistence jobPersistence,
                                     final String airbyteVersion) {
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.jobPersistence = jobPersistence;
    this.airbyteVersion = airbyteVersion;
  }

  public StandardCheckConnectionOutput check(final JobRunConfig jobRunConfig,
                                             final IntegrationLauncherConfig launcherConfig,
                                             final StandardCheckConnectionInput connectionConfiguration) {

    final JsonNode fullConfig = secretsHydrator.hydrate(connectionConfiguration.getConnectionConfiguration());

    final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
        .withConnectionConfiguration(fullConfig);

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<StandardCheckConnectionInput, StandardCheckConnectionOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot, workerEnvironment, logConfigs,
            jobRunConfig,
            getWorkerFactory(launcherConfig),
            () -> input,
            new CancellationHandler.TemporalCancellationHandler(context),
            jobPersistence,
            airbyteVersion,
            () -> context);

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<StandardCheckConnectionInput, StandardCheckConnectionOutput>, Exception> getWorkerFactory(
                                                                                                                           final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher = new AirbyteIntegrationLauncher(
          launcherConfig.getJobId(),
          Math.toIntExact(launcherConfig.getAttemptId()),
          launcherConfig.getDockerImage(),
          processFactory,
          workerConfigs.getResourceRequirements());

      return new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher);
    };
  }

}
