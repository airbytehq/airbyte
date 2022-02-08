/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Just like how the Linux bootloader paves the way for the OS to start, this class is responsible
 * for setting up the Airbyte environment so the rest of the Airbyte applications can safely start.
 * <p>
 * This includes:
 * <p>
 * - creating databases, if needed.
 * <p>
 * - ensuring all required database migrations are run.
 * <p>
 * - setting all required Airbyte metadata information.
 */
public class BootloaderApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(BootloaderApp.class);
  private static final AirbyteVersion VERSION_BREAK = new AirbyteVersion("0.32.0-alpha");

  private final Configs configs;
  private Runnable postLoadExecution;
  private FeatureFlags featureFlags;

  @VisibleForTesting
  public BootloaderApp(Configs configs, FeatureFlags featureFlags) {
    this.configs = configs;
    this.featureFlags = featureFlags;
  }

  /**
   * This method is exposed for Airbyte Cloud consumption. This lets us override the seed loading
   * logic and customise Cloud connector versions. Please check with the Platform team before making
   * changes to this method.
   *
   * @param configs
   * @param postLoadExecution
   */
  public BootloaderApp(Configs configs, Runnable postLoadExecution, FeatureFlags featureFlags) {
    this.configs = configs;
    this.postLoadExecution = postLoadExecution;
    this.featureFlags = featureFlags;
  }

  public BootloaderApp() {
    configs = new EnvConfigs();
    postLoadExecution = () -> {
      try {
        final Database configDatabase =
            new ConfigsDatabaseInstance(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(), configs.getConfigDatabaseUrl())
                .getAndInitialize();
        final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase);
        configPersistence.loadData(YamlSeedConfigPersistence.getDefault());
        LOGGER.info("Loaded seed data..");
      } catch (IOException e) {
        e.printStackTrace();
      }
    };
    featureFlags = new EnvVariableFeatureFlags();
  }

  public void load() throws Exception {
    LOGGER.info("Setting up config database and default workspace..");

    try (
        final Database configDatabase =
            new ConfigsDatabaseInstance(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(), configs.getConfigDatabaseUrl())
                .getAndInitialize();
        final Database jobDatabase =
            new JobsDatabaseInstance(configs.getDatabaseUser(), configs.getDatabasePassword(), configs.getDatabaseUrl()).getAndInitialize()) {
      LOGGER.info("Created initial jobs and configs database...");

      final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
      final AirbyteVersion currAirbyteVersion = configs.getAirbyteVersion();
      assertNonBreakingMigration(jobPersistence, currAirbyteVersion);

      runFlywayMigration(configs, configDatabase, jobDatabase);
      LOGGER.info("Ran Flyway migrations...");

      final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase);
      final ConfigRepository configRepository =
          new ConfigRepository(configPersistence, null, Optional.empty(), Optional.empty());

      createWorkspaceIfNoneExists(configRepository);
      LOGGER.info("Default workspace created..");

      createDeploymentIfNoneExists(jobPersistence);
      LOGGER.info("Default deployment created..");

      jobPersistence.setVersion(currAirbyteVersion.serialize());
      LOGGER.info("Set version to {}", currAirbyteVersion);
    }

    if (postLoadExecution != null) {
      postLoadExecution.run();
      LOGGER.info("Finished running post load Execution..");
    }

    LOGGER.info("Finished bootstrapping Airbyte environment..");
  }

  public static void main(String[] args) throws Exception {
    final var bootloader = new BootloaderApp();
    bootloader.load();
  }

  private static void createDeploymentIfNoneExists(final JobPersistence jobPersistence) throws IOException {
    final Optional<UUID> deploymentOptional = jobPersistence.getDeployment();
    if (deploymentOptional.isPresent()) {
      LOGGER.info("running deployment: {}", deploymentOptional.get());
    } else {
      final UUID deploymentId = UUID.randomUUID();
      jobPersistence.setDeployment(deploymentId);
      LOGGER.info("created deployment: {}", deploymentId);
    }
  }

  private static void createWorkspaceIfNoneExists(final ConfigRepository configRepository) throws JsonValidationException, IOException {
    if (!configRepository.listStandardWorkspaces(true).isEmpty()) {
      LOGGER.info("workspace already exists for the deployment.");
      return;
    }

    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withCustomerId(UUID.randomUUID())
        .withName(workspaceId.toString())
        .withSlug(workspaceId.toString())
        .withInitialSetupComplete(false)
        .withDisplaySetupWizard(true)
        .withTombstone(false);
    configRepository.writeStandardWorkspace(workspace);
  }

  private static void assertNonBreakingMigration(JobPersistence jobPersistence, AirbyteVersion airbyteVersion) throws IOException {
    // version in the database when the server main method is called. may be empty if this is the first
    // time the server is started.
    LOGGER.info("Checking illegal upgrade..");
    final Optional<AirbyteVersion> initialAirbyteDatabaseVersion = jobPersistence.getVersion().map(AirbyteVersion::new);
    if (!isLegalUpgrade(initialAirbyteDatabaseVersion.orElse(null), airbyteVersion)) {
      final String attentionBanner = MoreResources.readResource("banner/attention-banner.txt");
      LOGGER.error(attentionBanner);
      final String message = String.format(
          "Cannot upgrade from version %s to version %s directly. First you must upgrade to version %s. After that upgrade is complete, you may upgrade to version %s",
          initialAirbyteDatabaseVersion.get().serialize(),
          airbyteVersion.serialize(),
          VERSION_BREAK.serialize(),
          airbyteVersion.serialize());

      LOGGER.error(message);
      throw new RuntimeException(message);
    }
  }

  static boolean isLegalUpgrade(final AirbyteVersion airbyteDatabaseVersion, final AirbyteVersion airbyteVersion) {
    // means there was no previous version so upgrade even needs to happen. always legal.
    if (airbyteDatabaseVersion == null) {
      LOGGER.info("No previous Airbyte Version set..");
      return true;
    }

    LOGGER.info("Current Airbyte version: {}", airbyteDatabaseVersion);
    LOGGER.info("Future Airbyte version: {}", airbyteVersion);
    final var futureVersionIsAfterVersionBreak = airbyteVersion.greaterThan(VERSION_BREAK) || airbyteVersion.isDev();
    final var isUpgradingThroughVersionBreak = airbyteDatabaseVersion.lessThan(VERSION_BREAK) && futureVersionIsAfterVersionBreak;
    return !isUpgradingThroughVersionBreak;
  }

  private static void runFlywayMigration(final Configs configs, final Database configDatabase, final Database jobDatabase) {
    final DatabaseMigrator configDbMigrator = new ConfigsDatabaseMigrator(configDatabase, BootloaderApp.class.getSimpleName());
    final DatabaseMigrator jobDbMigrator = new JobsDatabaseMigrator(jobDatabase, BootloaderApp.class.getSimpleName());

    configDbMigrator.createBaseline();
    jobDbMigrator.createBaseline();

    if (configs.runDatabaseMigrationOnStartup()) {
      LOGGER.info("Migrating configs database");
      configDbMigrator.migrate();
      LOGGER.info("Migrating jobs database");
      jobDbMigrator.migrate();
    } else {
      LOGGER.info("Auto database migration is skipped");
    }
  }

  private static void cleanupZombies(final JobPersistence jobPersistence) throws IOException {
    final Configs configs = new EnvConfigs();
    WorkflowClient wfClient =
        WorkflowClient.newInstance(WorkflowServiceStubs.newInstance(
            WorkflowServiceStubsOptions.newBuilder().setTarget(configs.getTemporalHost()).build()));
    for (final Job zombieJob : jobPersistence.listJobsWithStatus(JobStatus.RUNNING)) {
      LOGGER.info("Kill zombie job {} for connection {}", zombieJob.getId(), zombieJob.getScope());
      wfClient.newUntypedWorkflowStub("sync_" + zombieJob.getId())
          .terminate("Zombie");
    }
  }

}
