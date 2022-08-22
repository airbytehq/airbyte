/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static io.airbyte.config.Configs.SecretPersistenceType.TESTING_CONFIG_DB_TABLE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseTestProvider;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import javax.sql.DataSource;
import lombok.val;
import org.flywaydb.core.Flyway;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.PostgreSQLContainer;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@SuppressWarnings("PMD.AvoidUsingHardCodedIP")
@ExtendWith(SystemStubsExtension.class)
class BootloaderAppTest {

  private PostgreSQLContainer container;
  private DataSource configsDataSource;
  private DataSource jobsDataSource;
  private static final String DOCKER = "docker";
  private static final String VERSION_0330_ALPHA = "0.33.0-alpha";
  private static final String VERSION_0320_ALPHA = "0.32.0-alpha";
  private static final String VERSION_0321_ALPHA = "0.32.1-alpha";
  private static final String VERSION_0170_ALPHA = "0.17.0-alpha";

  @BeforeEach
  void setup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("public")
        .withUsername(DOCKER)
        .withPassword(DOCKER);
    container.start();

    configsDataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
    jobsDataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
  }

  @AfterEach
  void cleanup() throws Exception {
    closeDataSource(configsDataSource);
    closeDataSource(jobsDataSource);
    container.stop();
  }

  @SystemStub
  private EnvironmentVariables environmentVariables;

  @Test
  void testBootloaderAppBlankDb() throws Exception {
    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(VERSION_0330_ALPHA));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);
    when(mockedConfigs.getConfigsDatabaseInitializationTimeoutMs()).thenReturn(60000L);
    when(mockedConfigs.getJobsDatabaseInitializationTimeoutMs()).thenReturn(60000L);

    val mockedFeatureFlags = mock(FeatureFlags.class);

    val mockedSecretMigrator = mock(SecretMigrator.class);

    // Although we are able to inject mocked configs into the Bootloader, a particular migration in the
    // configs database
    // requires the env var to be set. Flyway prevents injection, so we dynamically set this instead.
    environmentVariables.set("DATABASE_USER", DOCKER);
    environmentVariables.set("DATABASE_PASSWORD", DOCKER);
    environmentVariables.set("DATABASE_URL", container.getJdbcUrl());

    try (val configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        val jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {

      val configsFlyway = createConfigsFlyway(configsDataSource);
      val jobsFlyway = createJobsFlyway(jobsDataSource);

      val configDatabase = new ConfigsDatabaseTestProvider(configsDslContext, configsFlyway).create(false);
      val jobDatabase = new JobsDatabaseTestProvider(jobsDslContext, jobsFlyway).create(false);

      val bootloader =
          new BootloaderApp(mockedConfigs, mockedFeatureFlags, mockedSecretMigrator, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      bootloader.load();

      val jobsMigrator = new JobsDatabaseMigrator(jobDatabase, jobsFlyway);
      assertEquals("0.35.62.001", jobsMigrator.getLatestMigration().getVersion().getVersion());

      val configsMigrator = new ConfigsDatabaseMigrator(configDatabase, configsFlyway);
      // this line should change with every new migration
      // to show that you meant to make a new migration to the prod database
      assertEquals("0.39.17.001", configsMigrator.getLatestMigration().getVersion().getVersion());

      val jobsPersistence = new DefaultJobPersistence(jobDatabase);
      assertEquals(VERSION_0330_ALPHA, jobsPersistence.getVersion().get());

      assertNotEquals(Optional.empty(), jobsPersistence.getDeployment().get());
    }
  }

  @Test
  void testBootloaderAppRunSecretMigration() throws Exception {
    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(VERSION_0330_ALPHA));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);
    when(mockedConfigs.getSecretPersistenceType()).thenReturn(TESTING_CONFIG_DB_TABLE);
    when(mockedConfigs.getConfigsDatabaseInitializationTimeoutMs()).thenReturn(60000L);
    when(mockedConfigs.getJobsDatabaseInitializationTimeoutMs()).thenReturn(60000L);

    val mockedFeatureFlags = mock(FeatureFlags.class);

    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .copySecrets(true)
        .maskSecrets(true)
        .build();

    try (val configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        val jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {

      val configsFlyway = createConfigsFlyway(configsDataSource);
      val jobsFlyway = createJobsFlyway(jobsDataSource);

      val configDatabase = new ConfigsDatabaseTestProvider(configsDslContext, configsFlyway).create(false);
      val jobDatabase = new JobsDatabaseTestProvider(jobsDslContext, jobsFlyway).create(false);

      val configPersistence = new DatabaseConfigPersistence(configDatabase, jsonSecretsProcessor);
      val jobsPersistence = new DefaultJobPersistence(jobDatabase);

      val spiedSecretMigrator =
          spy(new SecretMigrator(configPersistence, jobsPersistence, SecretPersistence.getLongLived(configsDslContext, mockedConfigs)));

      // Although we are able to inject mocked configs into the Bootloader, a particular migration in the
      // configs database requires the env var to be set. Flyway prevents injection, so we dynamically set
      // this instead.
      environmentVariables.set("DATABASE_USER", DOCKER);
      environmentVariables.set("DATABASE_PASSWORD", DOCKER);
      environmentVariables.set("DATABASE_URL", container.getJdbcUrl());

      // Bootstrap the database for the test
      val initBootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, null, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      initBootloader.load();

      final ConfigPersistence localSchema = new YamlSeedConfigPersistence(YamlSeedConfigPersistence.DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);
      final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);
      configRepository.loadDataNoSecrets(localSchema);

      final String sourceSpecs = """
                                 {
                                   "account_id": "1234567891234567",
                                   "start_date": "2022-04-01T00:00:00Z",
                                   "access_token": "nonhiddensecret",
                                   "include_deleted": false,
                                   "fetch_thumbnail_images": false
                                 }

                                 """;

      final ObjectMapper mapper = new ObjectMapper();

      final UUID workspaceId = UUID.randomUUID();
      configRepository.writeStandardWorkspace(new StandardWorkspace()
          .withWorkspaceId(workspaceId)
          .withName("wName")
          .withSlug("wSlug")
          .withEmail("email@mail.com")
          .withTombstone(false)
          .withInitialSetupComplete(false));
      final UUID sourceId = UUID.randomUUID();
      configRepository.writeSourceConnectionNoSecrets(new SourceConnection()
          .withSourceDefinitionId(UUID.fromString("e7778cfc-e97c-4458-9ecb-b4f2bba8946c")) // Facebook Marketing
          .withSourceId(sourceId)
          .withName("test source")
          .withWorkspaceId(workspaceId)
          .withConfiguration(mapper.readTree(sourceSpecs)));

      when(mockedFeatureFlags.forceSecretMigration()).thenReturn(false);

      // Perform secrets migration
      var bootloader =
          new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      boolean isMigrated = jobsPersistence.isSecretMigrated();

      assertFalse(isMigrated);

      bootloader.load();
      verify(spiedSecretMigrator).migrateSecrets();

      final SourceConnection sourceConnection = configRepository.getSourceConnection(sourceId);

      assertFalse(sourceConnection.getConfiguration().toString().contains("nonhiddensecret"));
      assertTrue(sourceConnection.getConfiguration().toString().contains("_secret"));

      isMigrated = jobsPersistence.isSecretMigrated();
      assertTrue(isMigrated);

      // Verify that the migration does not happen if it has already been performed
      reset(spiedSecretMigrator);
      // We need to re-create the bootloader because it is closing the persistence after running load
      bootloader =
          new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      bootloader.load();
      verifyNoInteractions(spiedSecretMigrator);

      // Verify that the migration occurs if the force migration feature flag is enabled
      reset(spiedSecretMigrator);
      when(mockedFeatureFlags.forceSecretMigration()).thenReturn(true);
      // We need to re-create the bootloader because it is closing the persistence after running load
      bootloader =
          new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator, configsDslContext, jobsDslContext, configsFlyway, jobsFlyway);
      bootloader.load();
      verify(spiedSecretMigrator).migrateSecrets();
    }
  }

  @Test
  void testIsLegalUpgradePredicate() {
    // starting from no previous version is always legal.
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.17.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion(VERSION_0320_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion(VERSION_0321_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.33.1-alpha")));
    // starting from a version that is pre-breaking migration cannot go past the breaking migration.
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0170_ALPHA), new AirbyteVersion("0.17.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0170_ALPHA), new AirbyteVersion("0.18.0-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0170_ALPHA), new AirbyteVersion(VERSION_0320_ALPHA)));
    assertFalse(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0170_ALPHA), new AirbyteVersion(VERSION_0321_ALPHA)));
    assertFalse(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0170_ALPHA), new AirbyteVersion(VERSION_0330_ALPHA)));
    // any migration starting at the breaking migration or after it can upgrade to anything.
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0320_ALPHA), new AirbyteVersion(VERSION_0321_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0320_ALPHA), new AirbyteVersion(VERSION_0330_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0321_ALPHA), new AirbyteVersion(VERSION_0321_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0321_ALPHA), new AirbyteVersion(VERSION_0330_ALPHA)));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0330_ALPHA), new AirbyteVersion("0.33.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion(VERSION_0330_ALPHA), new AirbyteVersion("0.34.0-alpha")));
  }

  @Test
  void testPostLoadExecutionExecutes() throws Exception {
    final var testTriggered = new AtomicBoolean();
    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(VERSION_0330_ALPHA));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);
    when(mockedConfigs.getConfigsDatabaseInitializationTimeoutMs()).thenReturn(60000L);
    when(mockedConfigs.getJobsDatabaseInitializationTimeoutMs()).thenReturn(60000L);

    val mockedFeatureFlags = mock(FeatureFlags.class);

    val mockedSecretMigrator = mock(SecretMigrator.class);

    try (val configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        val jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {

      val configsFlyway = createConfigsFlyway(configsDataSource);
      val jobsFlyway = createJobsFlyway(jobsDataSource);

      new ConfigsDatabaseTestProvider(configsDslContext, configsFlyway).create(false);
      new JobsDatabaseTestProvider(jobsDslContext, jobsFlyway).create(false);

      new BootloaderApp(mockedConfigs, () -> testTriggered.set(true), mockedFeatureFlags, mockedSecretMigrator, configsDslContext, jobsDslContext,
          configsFlyway, jobsFlyway)
              .load();

      assertTrue(testTriggered.get());
    }
  }

  private Flyway createConfigsFlyway(final DataSource dataSource) {
    return FlywayFactory.create(dataSource, getClass().getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
  }

  private Flyway createJobsFlyway(final DataSource dataSource) {
    return FlywayFactory.create(dataSource, getClass().getName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
  }

  private void closeDataSource(final DataSource dataSource) throws Exception {
    DataSourceFactory.close(dataSource);
  }

}
