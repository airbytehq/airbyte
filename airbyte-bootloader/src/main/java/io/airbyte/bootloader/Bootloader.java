/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Geography;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.init.PostLoadExecutor;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.init.DatabaseInitializer;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

/**
 * Ensures that the databases are migrated to the appropriate level.
 */
@Singleton
@Slf4j
public class Bootloader {

  private static final AirbyteVersion VERSION_BREAK = new AirbyteVersion("0.32.0-alpha");

  private final boolean autoUpgradeConnectors;
  private final ConfigRepository configRepository;
  private final DatabaseMigrator configsDatabaseMigrator;
  private final DatabaseInitializer configsDatabaseInitializer;
  private final AirbyteVersion currentAirbyteVersion;
  private final Optional<DefinitionsProvider> definitionsProvider;
  private final FeatureFlags featureFlags;
  private final DatabaseInitializer jobsDatabaseInitializer;
  private final DatabaseMigrator jobsDatabaseMigrator;
  private final JobPersistence jobPersistence;
  private final PostLoadExecutor postLoadExecution;
  private final ProtocolVersionChecker protocolVersionChecker;
  private final boolean runMigrationOnStartup;
  private final SecretMigrator secretMigrator;

  public Bootloader(
                    @Value("${airbyte.bootloader.auto-upgrade-connectors}") final boolean autoUpgradeConnectors,
                    final ConfigRepository configRepository,
                    @Named("configsDatabaseInitializer") final DatabaseInitializer configsDatabaseInitializer,
                    @Named("configsDatabaseMigrator") final DatabaseMigrator configsDatabaseMigrator,
                    final AirbyteVersion currentAirbyteVersion,
                    final Optional<DefinitionsProvider> definitionsProvider,
                    final FeatureFlags featureFlags,
                    @Named("jobsDatabaseInitializer") final DatabaseInitializer jobsDatabaseInitializer,
                    @Named("jobsDatabaseMigrator") final DatabaseMigrator jobsDatabaseMigrator,
                    final JobPersistence jobPersistence,
                    final ProtocolVersionChecker protocolVersionChecker,
                    @Value("${airbyte.bootloader.run-migration-on-startup}") final boolean runMigrationOnStartup,
                    final SecretMigrator secretMigrator,
                    final PostLoadExecutor postLoadExecution) {
    this.autoUpgradeConnectors = autoUpgradeConnectors;
    this.configRepository = configRepository;
    this.configsDatabaseInitializer = configsDatabaseInitializer;
    this.configsDatabaseMigrator = configsDatabaseMigrator;
    this.currentAirbyteVersion = currentAirbyteVersion;
    this.definitionsProvider = definitionsProvider;
    this.featureFlags = featureFlags;
    this.jobsDatabaseInitializer = jobsDatabaseInitializer;
    this.jobsDatabaseMigrator = jobsDatabaseMigrator;
    this.jobPersistence = jobPersistence;
    this.protocolVersionChecker = protocolVersionChecker;
    this.runMigrationOnStartup = runMigrationOnStartup;
    this.secretMigrator = secretMigrator;
    this.postLoadExecution = postLoadExecution;
  }

  /**
   * Performs all required bootstrapping for the Airbyte environment. This includes the following:
   * <ul>
   * <li>Initializes the databases</li>
   * <li>Check database migration compatibility</li>
   * <li>Check protocol version compatibility</li>
   * <li>Migrate databases</li>
   * <li>Create default workspace</li>
   * <li>Create default deployment</li>
   * <li>Perform post migration tasks</li>
   * </ul>
   *
   * @throws Exception if unable to perform any of the bootstrap operations.
   */
  public void load() throws Exception {
    log.info("Initializing databases...");
    initializeDatabases();

    log.info("Checking migration compatibility...");
    assertNonBreakingMigration(jobPersistence, currentAirbyteVersion);

    log.info("Checking protocol version constraints...");
    assertNonBreakingProtocolVersionConstraints(protocolVersionChecker, jobPersistence, autoUpgradeConnectors);

    log.info("Running database migrations...");
    runFlywayMigration(runMigrationOnStartup, configsDatabaseMigrator, jobsDatabaseMigrator);

    log.info("Creating workspace (if none exists)...");
    createWorkspaceIfNoneExists(configRepository);

    log.info("Creating deployment (if none exists)...");
    createDeploymentIfNoneExists(jobPersistence);

    final String airbyteVersion = currentAirbyteVersion.serialize();
    log.info("Setting Airbyte version to '{}'...", airbyteVersion);
    jobPersistence.setVersion(airbyteVersion);
    log.info("Set version to '{}'", airbyteVersion);

    if (postLoadExecution != null) {
      postLoadExecution.execute();
      log.info("Finished running post load Execution.");
    }

    log.info("Finished bootstrapping Airbyte environment.");
  }

  private void assertNonBreakingMigration(final JobPersistence jobPersistence, final AirbyteVersion airbyteVersion)
      throws IOException {
    // version in the database when the server main method is called. may be empty if this is the first
    // time the server is started.
    log.info("Checking for illegal upgrade...");
    final Optional<AirbyteVersion> initialAirbyteDatabaseVersion = jobPersistence.getVersion().map(AirbyteVersion::new);
    if (!isLegalUpgrade(initialAirbyteDatabaseVersion.orElse(null), airbyteVersion)) {
      final String attentionBanner = MoreResources.readResource("banner/attention-banner.txt");
      log.error(attentionBanner);
      final String message = String.format(
          "Cannot upgrade from version %s to version %s directly. First you must upgrade to version %s. After that upgrade is complete, you may upgrade to version %s",
          initialAirbyteDatabaseVersion.get().serialize(),
          airbyteVersion.serialize(),
          VERSION_BREAK.serialize(),
          airbyteVersion.serialize());

      log.error(message);
      throw new RuntimeException(message);
    }
  }

  private void assertNonBreakingProtocolVersionConstraints(final ProtocolVersionChecker protocolVersionChecker,
                                                           final JobPersistence jobPersistence,
                                                           final boolean autoUpgradeConnectors)
      throws Exception {
    final Optional<AirbyteProtocolVersionRange> newProtocolRange = protocolVersionChecker.validate(autoUpgradeConnectors);
    if (newProtocolRange.isEmpty()) {
      throw new RuntimeException(
          "Aborting bootloader to avoid breaking existing connection after an upgrade. " +
              "Please address airbyte protocol version support issues in the connectors before retrying.");
    }
    trackProtocolVersion(jobPersistence, newProtocolRange.get());
  }

  private void createDeploymentIfNoneExists(final JobPersistence jobPersistence) throws IOException {
    final Optional<UUID> deploymentOptional = jobPersistence.getDeployment();
    if (deploymentOptional.isPresent()) {
      log.info("Running deployment: {}", deploymentOptional.get());
    } else {
      final UUID deploymentId = UUID.randomUUID();
      jobPersistence.setDeployment(deploymentId);
      log.info("Created deployment: {}", deploymentId);
    }
  }

  private void createWorkspaceIfNoneExists(final ConfigRepository configRepository) throws JsonValidationException, IOException {
    if (!configRepository.listStandardWorkspaces(true).isEmpty()) {
      log.info("Workspace already exists for the deployment.");
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
        .withTombstone(false)
        .withDefaultGeography(Geography.AUTO);
    // NOTE: it's safe to use the NoSecrets version since we know that the user hasn't supplied any
    // secrets yet.
    configRepository.writeStandardWorkspaceNoSecrets(workspace);
  }

  private void initializeDatabases() throws DatabaseInitializationException {
    log.info("Initializing databases...");
    configsDatabaseInitializer.initialize();
    jobsDatabaseInitializer.initialize();
    log.info("Databases initialized.");
  }

  @VisibleForTesting
  boolean isLegalUpgrade(final AirbyteVersion airbyteDatabaseVersion, final AirbyteVersion airbyteVersion) {
    // means there was no previous version so upgrade even needs to happen. always legal.
    if (airbyteDatabaseVersion == null) {
      log.info("No previous Airbyte Version set.");
      return true;
    }

    log.info("Current Airbyte version: {}", airbyteDatabaseVersion);
    log.info("Future Airbyte version: {}", airbyteVersion);
    final var futureVersionIsAfterVersionBreak = airbyteVersion.greaterThan(VERSION_BREAK) || airbyteVersion.isDev();
    final var isUpgradingThroughVersionBreak = airbyteDatabaseVersion.lessThan(VERSION_BREAK) && futureVersionIsAfterVersionBreak;
    return !isUpgradingThroughVersionBreak;
  }

  private void runFlywayMigration(final boolean runDatabaseMigrationOnStartup,
                                  final DatabaseMigrator configDbMigrator,
                                  final DatabaseMigrator jobDbMigrator) {
    log.info("Creating baseline for config database...");
    configDbMigrator.createBaseline();
    log.info("Creating baseline for job database...");
    jobDbMigrator.createBaseline();

    if (runDatabaseMigrationOnStartup) {
      log.info("Migrating configs database...");
      configDbMigrator.migrate();
      log.info("Migrating jobs database...");
      jobDbMigrator.migrate();
    } else {
      log.info("Auto database migration has been skipped.");
    }
  }

  private void trackProtocolVersion(final JobPersistence jobPersistence, final AirbyteProtocolVersionRange protocolVersionRange)
      throws IOException {
    jobPersistence.setAirbyteProtocolVersionMin(protocolVersionRange.min());
    jobPersistence.setAirbyteProtocolVersionMax(protocolVersionRange.max());
    log.info("AirbyteProtocol version support range: [{}:{}]", protocolVersionRange.min().serialize(), protocolVersionRange.max().serialize());
  }

}
