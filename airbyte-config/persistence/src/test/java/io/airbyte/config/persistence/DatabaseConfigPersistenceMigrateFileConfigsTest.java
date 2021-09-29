/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.Configs;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit test for the {@link DatabaseConfigPersistence#migrateFileConfigs} method.
 */
public class DatabaseConfigPersistenceMigrateFileConfigsTest extends BaseDatabaseConfigPersistenceTest {

  private static Path ROOT_PATH;
  private final Configs configs = mock(Configs.class);

  @BeforeAll
  public static void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));
  }

  @AfterAll
  public static void tearDown() throws Exception {
    database.close();
  }

  @BeforeEach
  public void resetPersistence() throws Exception {
    ROOT_PATH = Files.createTempDirectory(
        Files.createDirectories(Path.of("/tmp/airbyte_tests")),
        DatabaseConfigPersistenceMigrateFileConfigsTest.class.getSimpleName() + UUID.randomUUID());

    reset(configs);
    when(configs.getConfigRoot()).thenReturn(ROOT_PATH);

    database.query(ctx -> ctx.truncateTable("airbyte_configs").execute());

    reset(configPersistence);
  }

  @Test
  @DisplayName("When database is not initialized, and there is no local config dir, do nothing")
  public void testNewDeployment() throws Exception {
    configPersistence.migrateFileConfigs(configs);

    assertRecordCount(0);

    verify(configPersistence, never()).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, never()).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @DisplayName("When database is not initialized, and there is local config dir, copy from local dir")
  public void testMigrationDeployment() throws Exception {
    prepareLocalFilePersistence();

    configPersistence.migrateFileConfigs(configs);

    assertRecordCount(2);
    assertHasSource(SOURCE_GITHUB);
    assertHasDestination(DESTINATION_S3);

    verify(configPersistence, times(1)).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @DisplayName("When database has been initialized, do nothing")
  public void testUpdateDeployment() throws Exception {
    prepareLocalFilePersistence();
    writeSource(configPersistence, SOURCE_GITHUB);

    configPersistence.migrateFileConfigs(configs);

    assertRecordCount(1);
    assertHasSource(SOURCE_GITHUB);

    verify(configPersistence, never()).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, never()).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  private void prepareLocalFilePersistence() throws Exception {
    Files.createDirectories(ROOT_PATH.resolve(FileSystemConfigPersistence.CONFIG_DIR));
    ConfigPersistence filePersistence = new FileSystemConfigPersistence(ROOT_PATH);
    writeSource(filePersistence, SOURCE_GITHUB);
    writeDestination(filePersistence, DESTINATION_S3);
  }

}
