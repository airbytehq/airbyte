/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import lombok.val;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.PostgreSQLContainer;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class BootloaderAppTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  @Test
  void testBootloaderAppBlankDb() throws Exception {
    val container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("public")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    val version = "0.33.0-alpha";

    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(version));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);

    val mockedFeatureFlags = mock(FeatureFlags.class);
    when(mockedFeatureFlags.usesNewScheduler()).thenReturn(false);

    val mockedSecretMigrator = mock(SecretMigrator.class);

    // Although we are able to inject mocked configs into the Bootloader, a particular migration in the
    // configs database
    // requires the env var to be set. Flyway prevents injection, so we dynamically set this instead.
    environmentVariables.set("DATABASE_USER", "docker");
    environmentVariables.set("DATABASE_PASSWORD", "docker");
    environmentVariables.set("DATABASE_URL", container.getJdbcUrl());

    val bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags);
    bootloader.load();

    try (val configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        val jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {

      val bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, mockedSecretMigrator, configsDslContext);
      bootloader.load(configsDataSource, jobsDataSource, jobsDslContext);

      val jobDatabase = new JobsDatabaseInstance(jobsDslContext).getInitialized();
      val jobsFlyway = FlywayFactory.create(jobsDataSource, getClass().getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
          JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
      val jobsMigrator = new JobsDatabaseMigrator(jobDatabase, jobsFlyway);
      assertEquals("0.35.62.001", jobsMigrator.getLatestMigration().getVersion().getVersion());

      val configDatabase = new ConfigsDatabaseInstance(configsDslContext).getAndInitialize();
      val configsFlyway = FlywayFactory.create(configsDataSource, getClass().getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
          ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
      val configsMigrator = new ConfigsDatabaseMigrator(configDatabase, configsFlyway);
      assertEquals("0.35.65.001", configsMigrator.getLatestMigration().getVersion().getVersion());

      val jobsPersistence = new DefaultJobPersistence(jobDatabase);
      assertEquals(version, jobsPersistence.getVersion().get());

      assertNotEquals(Optional.empty(), jobsPersistence.getDeployment().get());
    }
  }

  @Test
  void testBootloaderAppRunSecretMigration() throws Exception {
    val container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("public")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    val version = "0.33.0-alpha";

    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(version));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);
    when(mockedConfigs.getSecretPersistenceType()).thenReturn(TESTING_CONFIG_DB_TABLE);

    val mockedFeatureFlags = mock(FeatureFlags.class);
    when(mockedFeatureFlags.usesNewScheduler()).thenReturn(false);

    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .copySecrets(true)
        .maskSecrets(true)
        .build();
    final Database configDatabase = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase, jsonSecretsProcessor);

    val jobsPersistence = new DefaultJobPersistence(configDatabase);

    val spiedSecretMigrator = spy(new SecretMigrator(configPersistence, jobsPersistence, SecretPersistence.getLongLived(mockedConfigs)));

    // Although we are able to inject mocked configs into the Bootloader, a particular migration in the
    // configs database
    // requires the env var to be set. Flyway prevents injection, so we dynamically set this instead.
    environmentVariables.set("DATABASE_USER", "docker");
    environmentVariables.set("DATABASE_PASSWORD", "docker");
    environmentVariables.set("DATABASE_URL", container.getJdbcUrl());

    val initBootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags);
    initBootloader.load();

    final ConfigPersistence localSchema = YamlSeedConfigPersistence.getDefault();
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);
    configRepository.loadDataNoSecrets(localSchema);

      final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
          .copySecrets(true)
          .maskSecrets(true)
          .build();
      final Database configDatabase = new Database(configsDslContext);
      final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase, jsonSecretsProcessor);
      final ConfigPersistence localSchema = YamlSeedConfigPersistence.getDefault();
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

    when(mockedFeatureFlags.forceSecretMigration()).thenReturn(false);
    final var bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator);
    boolean isMigrated = jobsPersistence.isSecretMigrated();

    assertFalse(isMigrated);

    bootloader.load();
    verify(spiedSecretMigrator).migrateSecrets();

      when(mockedFeatureFlags.runSecretMigration()).thenReturn(true);
      val bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, configsDslContext);
      bootloader.load(configsDataSource, jobsDataSource, jobsDslContext);

    assertFalse(sourceConnection.getConfiguration().toString().contains("nonhiddensecret"));
    assertTrue(sourceConnection.getConfiguration().toString().contains("_secret"));

    isMigrated = jobsPersistence.isSecretMigrated();
    assertTrue(isMigrated);

    reset(spiedSecretMigrator);
    // We need to re-create the bootloader because it is closing the persistence after running load
    bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator);
    bootloader.load();
    verifyNoInteractions(spiedSecretMigrator);

    reset(spiedSecretMigrator);
    when(mockedFeatureFlags.forceSecretMigration()).thenReturn(true);
    // We need to re-create the bootloader because it is closing the persistence after running load
    bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags, spiedSecretMigrator);
    bootloader.load();
    verify(spiedSecretMigrator).migrateSecrets();
  }

  @Test
  void testIsLegalUpgradePredicate() {
    // starting from no previous version is always legal.
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.17.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.32.0-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.32.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(null, new AirbyteVersion("0.33.1-alpha")));
    // starting from a version that is pre-breaking migration cannot go past the breaking migration.
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.17.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.18.0-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.0-alpha")));
    assertFalse(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertFalse(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    // any migration starting at the breaking migration or after it can upgrade to anything.
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.33.1-alpha")));
    assertTrue(BootloaderApp.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.34.0-alpha")));
  }

  @Test
  void testPostLoadExecutionExecutes() throws Exception {
    final var testTriggered = new AtomicBoolean();

    val container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("public")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    val version = "0.33.0-alpha";

    val mockedConfigs = mock(Configs.class);
    when(mockedConfigs.getConfigDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getConfigDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getConfigDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());
    when(mockedConfigs.getDatabaseUser()).thenReturn(container.getUsername());
    when(mockedConfigs.getDatabasePassword()).thenReturn(container.getPassword());
    when(mockedConfigs.getAirbyteVersion()).thenReturn(new AirbyteVersion(version));
    when(mockedConfigs.runDatabaseMigrationOnStartup()).thenReturn(true);

    val mockedFeatureFlags = mock(FeatureFlags.class);
    when(mockedFeatureFlags.usesNewScheduler()).thenReturn(false);

    val mockedSecretMigrator = mock(SecretMigrator.class);

    val configsDataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
    val jobsDataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());

    try (val configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        val jobsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES)) {
      new BootloaderApp(mockedConfigs, () -> testTriggered.set(true), mockedFeatureFlags, mockedSecretMigrator, configsDslContext)
          .load(configsDataSource, jobsDataSource, jobsDslContext);

      assertTrue(testTriggered.get());
    }
  }

}
