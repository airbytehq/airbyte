/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
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
  private static final String DRIVER_CLASS_NAME = DatabaseDriver.POSTGRESQL.getDriverClassName();

  private final Configs configs;
  private final Runnable postLoadExecution;
  private final FeatureFlags featureFlags;
  private final SecretMigrator secretMigrator;
  private ConfigPersistence configPersistence;
  private Database configDatabase;
  private Database jobDatabase;
  private JobPersistence jobPersistence;
  private final Flyway configsFlyway;
  private final Flyway jobsFlyway;

  /**
   * This method is exposed for Airbyte Cloud consumption. This lets us override the seed loading
   * logic and customise Cloud connector versions. Please check with the Platform team before making
   * changes to this method.
   *
   * @param configs
   * @param postLoadExecution
   * @param featureFlags
   * @param secretMigrator
   * @param configsDslContext
   */
  public BootloaderApp(final Configs configs,
                       final Runnable postLoadExecution,
                       final FeatureFlags featureFlags,
                       final SecretMigrator secretMigrator,
                       final DSLContext configsDslContext,
                       final DSLContext jobsDslContext,
                       final Flyway configsFlyway,
                       final Flyway jobsFlyway) {
    this.configs = configs;
    this.postLoadExecution = postLoadExecution;
    this.featureFlags = featureFlags;
    this.secretMigrator = secretMigrator;
    this.configsFlyway = configsFlyway;
    this.jobsFlyway = jobsFlyway;

    initPersistences(configsDslContext, jobsDslContext);
  }

  public BootloaderApp(final Configs configs,
                       final FeatureFlags featureFlags,
                       final SecretMigrator secretMigrator,
                       final DSLContext configsDslContext,
                       final DSLContext jobsDslContext,
                       final Flyway configsFlyway,
                       final Flyway jobsFlyway) {
    this.configs = configs;
    this.featureFlags = featureFlags;
    this.secretMigrator = secretMigrator;
    this.configsFlyway = configsFlyway;
    this.jobsFlyway = jobsFlyway;

    initPersistences(configsDslContext, jobsDslContext);

    postLoadExecution = () -> {
      try {
        configPersistence.loadData(YamlSeedConfigPersistence.getDefault());

        if (featureFlags.forceSecretMigration() || !jobPersistence.isSecretMigrated()) {
          if (this.secretMigrator != null) {
            this.secretMigrator.migrateSecrets();
            LOGGER.info("Secrets successfully migrated.");
          }
        }
        LOGGER.info("Loaded seed data..");
      } catch (final IOException | JsonValidationException e) {
        throw new RuntimeException(e);
      }
    };
  }

  public void load() throws Exception {
    LOGGER.info("Setting up config database and default workspace...");
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
    final AirbyteVersion currAirbyteVersion = configs.getAirbyteVersion();
    assertNonBreakingMigration(jobPersistence, currAirbyteVersion);

    // TODO Will be converted to an injected singleton during DI migration
    final DatabaseMigrator configDbMigrator = new ConfigsDatabaseMigrator(configDatabase, configsFlyway);
    final DatabaseMigrator jobDbMigrator = new JobsDatabaseMigrator(jobDatabase, jobsFlyway);

    runFlywayMigration(configs, configDbMigrator, jobDbMigrator);
    LOGGER.info("Ran Flyway migrations.");

    final ConfigRepository configRepository =
        new ConfigRepository(configPersistence, configDatabase);

    createWorkspaceIfNoneExists(configRepository);
    LOGGER.info("Default workspace created.");

    createDeploymentIfNoneExists(jobPersistence);
    LOGGER.info("Default deployment created.");

    jobPersistence.setVersion(currAirbyteVersion.serialize());
    LOGGER.info("Set version to {}", currAirbyteVersion);

    postLoadExecution.run();

    LOGGER.info("Finished running post load Execution.");

    LOGGER.info("Finished bootstrapping Airbyte environment.");
  }

  private static Database getConfigDatabase(final DSLContext dslContext) throws IOException {
    return new ConfigsDatabaseInstance(dslContext).getAndInitialize();
  }

  private static ConfigPersistence getConfigPersistence(final Database configDatabase) throws IOException {
    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(true)
        .copySecrets(true)
        .build();

    return DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
  }

  private static Database getJobDatabase(final DSLContext dslContext) throws IOException {
    return new JobsDatabaseInstance(dslContext).getAndInitialize();
  }

  private static JobPersistence getJobPersistence(final Database jobDatabase) throws IOException {
    return new DefaultJobPersistence(jobDatabase);
  }

  private void initPersistences(final DSLContext configsDslContext, final DSLContext jobsDslContext) {
    try {
      configDatabase = getConfigDatabase(configsDslContext);
      configPersistence = getConfigPersistence(configDatabase);
      jobDatabase = getJobDatabase(jobsDslContext);
      jobPersistence = getJobPersistence(jobDatabase);
    } catch (final IOException e) {
      LOGGER.error("Unable to initialize persistence.", e);
    }
  }

  public static void main(final String[] args) throws Exception {
    final Configs configs = new EnvConfigs();
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

    // Manual configuration that will be replaced by Dependency Injection in the future
    final DataSource configsDataSource = DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(),
        DRIVER_CLASS_NAME, configs.getConfigDatabaseUrl());
    final DataSource jobsDataSource =
        DataSourceFactory.create(configs.getDatabaseUser(), configs.getDatabasePassword(), DRIVER_CLASS_NAME, configs.getDatabaseUrl());

    try (final DSLContext configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        final DSLContext jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {

      // TODO Will be converted to an injected singleton during DI migration
      final Database configDatabase = getConfigDatabase(configsDslContext);
      final ConfigPersistence configPersistence = getConfigPersistence(configDatabase);
      final Database jobDatabase = getJobDatabase(jobsDslContext);
      final JobPersistence jobPersistence = getJobPersistence(jobDatabase);
      final SecretMigrator secretMigrator =
          new SecretMigrator(configPersistence, jobPersistence, SecretPersistence.getLongLived(configsDslContext, configs));
      final Flyway configsFlyway = FlywayFactory.create(configsDataSource, BootloaderApp.class.getSimpleName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
          ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
      final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, BootloaderApp.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
          JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);

      // Ensure that the database resources are closed on application shutdown
      CloseableShutdownHook.registerRuntimeShutdownHook(configsDataSource, jobsDataSource, configsDslContext, jobsDslContext);

      final var bootloader = new BootloaderApp(configs, featureFlags, secretMigrator, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      bootloader.load();
    }
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

  private static void assertNonBreakingMigration(final JobPersistence jobPersistence, final AirbyteVersion airbyteVersion)
      throws IOException {
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

  private static void runFlywayMigration(final Configs configs, final DatabaseMigrator configDbMigrator, final DatabaseMigrator jobDbMigrator) {
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

}
