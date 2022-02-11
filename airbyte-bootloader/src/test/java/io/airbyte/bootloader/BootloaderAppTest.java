/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import lombok.val;
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

    // Although we are able to inject mocked configs into the Bootloader, a particular migration in the
    // configs database
    // requires the env var to be set. Flyway prevents injection, so we dynamically set this instead.
    environmentVariables.set("DATABASE_USER", "docker");
    environmentVariables.set("DATABASE_PASSWORD", "docker");
    environmentVariables.set("DATABASE_URL", container.getJdbcUrl());

    val bootloader = new BootloaderApp(mockedConfigs, mockedFeatureFlags);
    bootloader.load();

    val jobDatabase = new JobsDatabaseInstance(
        container.getUsername(),
        container.getPassword(),
        container.getJdbcUrl()).getInitialized();
    val jobsMigrator = new JobsDatabaseMigrator(jobDatabase, this.getClass().getName());
    assertEquals("0.35.5.001", jobsMigrator.getLatestMigration().getVersion().getVersion());

    val configDatabase = new ConfigsDatabaseInstance(
        mockedConfigs.getConfigDatabaseUser(),
        mockedConfigs.getConfigDatabasePassword(),
        mockedConfigs.getConfigDatabaseUrl())
            .getAndInitialize();
    val configsMigrator = new ConfigsDatabaseMigrator(configDatabase, this.getClass().getName());
    assertEquals("0.35.15.001", configsMigrator.getLatestMigration().getVersion().getVersion());

    val jobsPersistence = new DefaultJobPersistence(jobDatabase);
    assertEquals(version, jobsPersistence.getVersion().get());

    assertNotEquals(Optional.empty(), jobsPersistence.getDeployment().get());
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
    var testTriggered = new AtomicBoolean();

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

    new BootloaderApp(mockedConfigs, () -> testTriggered.set(true), mockedFeatureFlags).load();

    assertTrue(testTriggered.get());
  }

}
