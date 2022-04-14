/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.StartupEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import javax.annotation.PostConstruct;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
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
@Singleton
public class Bootloader {

  private static final Logger LOGGER = LoggerFactory.getLogger(Bootloader.class);

  private static final AirbyteVersion VERSION_BREAK = new AirbyteVersion("0.32.0-alpha");

  @Inject
  private AirbyteVersion currentAirbyteVersion;

  @Inject
  private ConfigPersistence configPersistence;

  @Inject
  private ConfigRepository configRepository;

  @Inject
  private FeatureFlags featureFlags;

  @Inject
  @Named("config")
  private DataSource configDataSource;

  @Inject
  @Named("jobs")
  private DataSource jobsDataSource;

  @Inject
  @Named("configFlyway")
  private Flyway configFlyway;

  @Inject
  @Named("jobsFlyway")
  private Flyway jobsFlyway;

  @Inject
  private JobPersistence jobPersistence;

  @Value("${airbyte.run_migration_on_startup}")
  private boolean runMigrationOnStartup;

  private Runnable postLoadExecution;

  @PostConstruct
  public void afterInitialization() {
    postLoadExecution = () -> {
      try {
        configPersistence.loadData(YamlSeedConfigPersistence.getDefault());
        LOGGER.info("Loaded seed data..");
      } catch (final IOException e) {
        LOGGER.error("Unable to load seed configuration data.", e);
      }
    };
  }

  @EventListener
  public void onStartup(final StartupEvent startupEvent) throws IOException, JsonValidationException {
    LOGGER.info("Setting up config database and default workspace...");
    assertNonBreakingMigration(jobPersistence, currentAirbyteVersion);

    runFlywayMigration(); // configs, configDatabase, jobDatabase);
    LOGGER.info("Ran Flyway migrations.");

    createWorkspaceIfNoneExists(configRepository);
    LOGGER.info("Default workspace created.");

    createDeploymentIfNoneExists(jobPersistence);
    LOGGER.info("Default deployment created.");

    jobPersistence.setVersion(currentAirbyteVersion.serialize());
    LOGGER.info("Set version to {}", currentAirbyteVersion);

    if (postLoadExecution != null) {
      postLoadExecution.run();
      LOGGER.info("Finished running post load Execution.");
    }

    LOGGER.info("Finished bootstrapping Airbyte environment.");
    System.exit(0);
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
    LOGGER.info("Checking illegal upgrade...");
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
      LOGGER.info("No previous Airbyte Version set.");
      return true;
    }

    LOGGER.info("Current Airbyte version: {}", airbyteDatabaseVersion);
    LOGGER.info("Future Airbyte version: {}", airbyteVersion);
    final var futureVersionIsAfterVersionBreak = airbyteVersion.greaterThan(VERSION_BREAK) || airbyteVersion.isDev();
    final var isUpgradingThroughVersionBreak = airbyteDatabaseVersion.lessThan(VERSION_BREAK) && futureVersionIsAfterVersionBreak;
    return !isUpgradingThroughVersionBreak;
  }

  private void runFlywayMigration() {
    configFlyway.baseline();
    jobsFlyway.baseline();

    if (runMigrationOnStartup) {
      LOGGER.info("Migrating configs database");
      configFlyway.migrate();
      LOGGER.info("Migrating jobs database");
      jobsFlyway.migrate();
    } else {
      LOGGER.info("Auto database migration is skipped");
    }
  }

}
