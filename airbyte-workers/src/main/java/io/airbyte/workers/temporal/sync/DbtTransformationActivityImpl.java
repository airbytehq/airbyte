package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DbtTransformationRunner;
import io.airbyte.workers.DbtTransformationWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DbtTransformationActivityImpl implements DbtTransformationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationActivityImpl.class);

  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final AirbyteConfigValidator validator;

  public DbtTransformationActivityImpl(
      final ProcessFactory processFactory,
      final SecretsHydrator secretsHydrator,
      final Path workspaceRoot) {
    this(processFactory, secretsHydrator, workspaceRoot, new AirbyteConfigValidator());
  }

  @VisibleForTesting DbtTransformationActivityImpl(final ProcessFactory processFactory,
                                                   final SecretsHydrator secretsHydrator,
                                                   final Path workspaceRoot,
                                                   final AirbyteConfigValidator validator) {
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.validator = validator;
  }

  @Override
  public Void run(final JobRunConfig jobRunConfig,
                  final IntegrationLauncherConfig destinationLauncherConfig,
                  final ResourceRequirements resourceRequirements,
                  final OperatorDbtInput input) {

    final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
    final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

    final Supplier<OperatorDbtInput> inputSupplier = () -> {
      validator.ensureAsRuntime(ConfigSchema.OPERATOR_DBT_INPUT, Jsons.jsonNode(fullInput));
      return fullInput;
    };

    final TemporalAttemptExecution<OperatorDbtInput, Void> temporalAttemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        jobRunConfig,
        getWorkerFactory(destinationLauncherConfig, jobRunConfig, resourceRequirements),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler());

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<OperatorDbtInput, Void>, Exception> getWorkerFactory(final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                      final JobRunConfig jobRunConfig,
                                                                                      final ResourceRequirements resourceRequirements) {
    return () -> new DbtTransformationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        resourceRequirements,
        new DbtTransformationRunner(
            processFactory, NormalizationRunnerFactory.create(
            destinationLauncherConfig.getDockerImage(),
            processFactory)));
  }
}
