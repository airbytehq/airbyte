/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;

public class CheckConnectionActivityImpl implements CheckConnectionActivity {

  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;

  public CheckConnectionActivityImpl(final ProcessFactory processFactory, final SecretsHydrator secretsHydrator, final Path workspaceRoot) {
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
  }

  public StandardCheckConnectionOutput run(final JobRunConfig jobRunConfig,
                                           final IntegrationLauncherConfig launcherConfig,
                                           final StandardCheckConnectionInput connectionConfiguration) {

    final JsonNode fullConfig = secretsHydrator.hydrate(connectionConfiguration.getConnectionConfiguration());

    final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
        .withConnectionConfiguration(fullConfig);

    final Supplier<StandardCheckConnectionInput> inputSupplier = () -> input;

    final TemporalAttemptExecution<StandardCheckConnectionInput, StandardCheckConnectionOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot,
            jobRunConfig,
            getWorkerFactory(launcherConfig),
            inputSupplier,
            new CancellationHandler.TemporalCancellationHandler());

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
          WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

      return new DefaultCheckConnectionWorker(integrationLauncher);
    };
  }

}
