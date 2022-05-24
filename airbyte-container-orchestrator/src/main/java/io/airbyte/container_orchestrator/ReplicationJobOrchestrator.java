/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.instance.DatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.general.DefaultReplicationWorker;
import io.airbyte.workers.general.ReplicationWorker;
import io.airbyte.workers.internal.AirbyteMessageTracker;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.EmptyAirbyteSource;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.sync.ReplicationLauncherWorker;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import javax.sql.DataSource;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;

@Slf4j
public class ReplicationJobOrchestrator implements JobOrchestrator<StandardSyncInput> {

  private final ProcessFactory processFactory;
  private final WorkerConfigs workerConfigs;
  private final Configs configs;

  public ReplicationJobOrchestrator(final Configs configs, final WorkerConfigs workerConfigs, final ProcessFactory processFactory) {
    this.configs = configs;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
  }

  @Override
  public String getOrchestratorName() {
    return "Replication";
  }

  @Override
  public Class<StandardSyncInput> getInputClass() {
    return StandardSyncInput.class;
  }

  @Override
  public Optional<String> runJob() throws Exception {
    final JobRunConfig jobRunConfig = JobOrchestrator.readJobRunConfig();
    final StandardSyncInput syncInput = readInput();

    final IntegrationLauncherConfig sourceLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_SOURCE_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    final IntegrationLauncherConfig destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    log.info("Setting up source launcher...");
    final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
        sourceLauncherConfig.getJobId(),
        Math.toIntExact(sourceLauncherConfig.getAttemptId()),
        sourceLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getSourceResourceRequirements());

    log.info("Setting up destination launcher...");
    final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
        destinationLauncherConfig.getJobId(),
        Math.toIntExact(destinationLauncherConfig.getAttemptId()),
        destinationLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getDestinationResourceRequirements());

    log.info("Setting up source...");
    // reset jobs use an empty source to induce resetting all data in destination.
    final AirbyteSource airbyteSource =
        sourceLauncherConfig.getDockerImage().equals(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB) ? new EmptyAirbyteSource()
            : new DefaultAirbyteSource(workerConfigs, sourceLauncher);

    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
    final String driverClassName = "org.postgresql.Driver";
    final DataSource configsDataSource =
        DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(), driverClassName,
            configs.getConfigDatabaseUrl());
    final DSLContext configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
    final DatabaseInstance configsDatabaseInstance =
        new ConfigsDatabaseInstance(configsDslContext);
    final Database configDatabase = configsDatabaseInstance.getInitialized();
    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
    final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);
    final JobPersistence jobPersistence = new DefaultJobPersistence(configDatabase);
    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);
    final UUID workspaceId = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(Long.valueOf(jobRunConfig.getJobId()));

    log.info("Setting up replication worker...");
    final ReplicationWorker replicationWorker = new DefaultReplicationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        new DefaultAirbyteDestination(workerConfigs, destinationLauncher),
        new AirbyteMessageTracker(),
        new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput)),
        workspaceId,
        sourceLauncherConfig.getDockerImage());

    log.info("Running replication worker...");
    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    log.info("Returning output...");
    return Optional.of(Jsons.serialize(replicationOutput));
  }

}
