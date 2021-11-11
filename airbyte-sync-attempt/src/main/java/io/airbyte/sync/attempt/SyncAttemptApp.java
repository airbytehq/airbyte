/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.sync.attempt;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.*;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.sync.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SyncAttemptApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncAttemptApp.class);

  private final ReplicationActivity replicationActivity;
  private final NormalizationActivity normalizationActivity;
  private final DbtTransformationActivity dbtTransformationActivity;
  private final PersistStateActivity persistActivity;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final Configs.WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final String databaseUser;
  private final String databasePassword;
  private final String databaseUrl;
  private final String airbyteVersion;
  private final ConfigRepository configRepository;

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
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.databaseUser = databaseUser;
    this.databasePassword = databasePassword;
    this.databaseUrl = databaseUrl;
    this.airbyteVersion = airbyteVersion;
    this.configRepository = configRepository;

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

  public static void main(String[] args) throws IOException {
    final Configs configs = new EnvConfigs();

    // set up app

    // todo: figure out where to send these logs
    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot()));

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configs);

    final ProcessFactory processFactory = WorkerApp.getProcessBuilderFactory(configs);

    // todo: DRY this? also present in WorkerApp
    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase).withValidation();
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configs);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, secretsHydrator, secretPersistence, ephemeralSecretPersistence);

    final SyncAttemptApp app = new SyncAttemptApp(
        processFactory,
        secretsHydrator,
        configs.getWorkspaceRoot(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl(),
        configs.getAirbyteVersionOrWarning(),
        configRepository);

    // retrieve files
    // todo: don't use magic strings
    final JobRunConfig jobRunConfig = Jsons.deserialize(Files.readString(Path.of("jobRunConfig.json")), JobRunConfig.class);
    final IntegrationLauncherConfig sourceLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of("sourceLauncherConfig.json")), IntegrationLauncherConfig.class);
    final IntegrationLauncherConfig destinationLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of("destinationLauncherConfig.json")), IntegrationLauncherConfig.class);
    final StandardSyncInput syncInput = Jsons.deserialize(Files.readString(Path.of("syncInput.json")), StandardSyncInput.class);
    final UUID connectionId = Jsons.deserialize(Files.readString(Path.of("connectionId.json")), UUID.class); // todo: does this work?

    app.run(
        jobRunConfig,
        sourceLauncherConfig,
        destinationLauncherConfig,
        syncInput,
        connectionId);
  }

}
