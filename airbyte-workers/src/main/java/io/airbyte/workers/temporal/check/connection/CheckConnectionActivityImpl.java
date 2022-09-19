/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultCheckConnectionWorker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
@Requires(property = "airbyte.worker.plane",
          pattern = "(?i)^(?!data_plane).*")
public class CheckConnectionActivityImpl implements CheckConnectionActivity {

  @Inject
  @Named("checkWorkerConfigs")
  private WorkerConfigs workerConfigs;
  @Inject
  @Named("checkProcessFactory")
  private ProcessFactory processFactory;
  @Inject
  private SecretsHydrator secretsHydrator;
  @Inject
  @Named("workspaceRoot")
  private Path workspaceRoot;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Inject
  private LogConfigs logConfigs;
  @Inject
  private AirbyteApiClient airbyteApiClient;
  @Value("${airbyte.version}")
  private String airbyteVersion;

  @Override
  public ConnectorJobOutput runWithJobOutput(final CheckConnectionInput args) {
    final JsonNode fullConfig = secretsHydrator.hydrate(args.getConnectionConfiguration().getConnectionConfiguration());

    final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
        .withConnectionConfiguration(fullConfig);

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<StandardCheckConnectionInput, ConnectorJobOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot, workerEnvironment, logConfigs,
            args.getJobRunConfig(),
            getWorkerFactory(args.getLauncherConfig()),
            () -> input,
            new CancellationHandler.TemporalCancellationHandler(context),
            airbyteApiClient,
            airbyteVersion,
            () -> context);

    return temporalAttemptExecution.get();
  }

  @Override
  public StandardCheckConnectionOutput run(final CheckConnectionInput args) {
    final ConnectorJobOutput output = runWithJobOutput(args);
    if (output.getFailureReason() != null) {
      return new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("Error checking connection");
    }

    return output.getCheckConnection();
  }

  private CheckedSupplier<Worker<StandardCheckConnectionInput, ConnectorJobOutput>, Exception> getWorkerFactory(
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
