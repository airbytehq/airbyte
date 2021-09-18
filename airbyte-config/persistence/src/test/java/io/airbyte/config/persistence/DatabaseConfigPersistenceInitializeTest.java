/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;

/**
 * Unit test for the {@link DatabaseConfigPersistence#initialize} method.
 */
public class DatabaseConfigPersistenceInitializeTest extends BaseDatabaseConfigPersistenceTest {

  // mock YAML seed connector definitions
  private static final List<StandardSourceDefinition> SEED_SOURCES = List.of(SOURCE_GITHUB);
  private static final List<StandardDestinationDefinition> SEED_DESTINATIONS = List.of(DESTINATION_SNOWFLAKE);

  private static final ConfigPersistence SEED_PERSISTENCE = mock(ConfigPersistence.class);
  private static Path ROOT_PATH;

  private final Configs configs = mock(Configs.class);

  @BeforeAll
  public static void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));

    when(SEED_PERSISTENCE.dumpConfigs()).thenReturn(Map.of(
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), SEED_SOURCES.stream().map(Jsons::jsonNode),
        ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(), SEED_DESTINATIONS.stream().map(Jsons::jsonNode)));
    when(SEED_PERSISTENCE.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(SEED_SOURCES);
    when(SEED_PERSISTENCE.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(SEED_DESTINATIONS);
  }

  @AfterAll
  public static void tearDown() throws Exception {
    database.close();
  }

  @BeforeEach
  public void resetPersistence() throws Exception {
    ROOT_PATH = Files.createTempDirectory(
        Files.createDirectories(Path.of("/tmp/airbyte_tests")),
        DatabaseConfigPersistenceInitializeTest.class.getSimpleName() + UUID.randomUUID());

    reset(configs);
    when(configs.getConfigRoot()).thenReturn(ROOT_PATH);

    database.query(ctx -> ctx.truncateTable("airbyte_configs").execute());

    reset(configPersistence);
  }

  @Test
  @DisplayName("When database is not initialized, and there is no local config dir, copy from seed")
  public void testNewDeployment() throws Exception {
    configPersistence.initialize(configs, SEED_PERSISTENCE);

    assertRecordCount(2);
    assertHasSource(SOURCE_GITHUB);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    verify(configPersistence, times(1)).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, never()).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @DisplayName("When database is not initialized, and there is local config dir, copy from local and update from seed")
  public void testMigrationDeployment() throws Exception {
    prepareLocalFilePersistence();

    configPersistence.initialize(configs, SEED_PERSISTENCE);

    assertRecordCount(3);
    assertHasSource(SOURCE_GITHUB);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    InOrder callOrder = inOrder(configPersistence);
    callOrder.verify(configPersistence, times(1)).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    callOrder.verify(configPersistence, times(1)).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @DisplayName("When database has been initialized, ignore local config dir, and update from seed")
  public void testUpdateDeployment() throws Exception {
    prepareLocalFilePersistence();
    writeSource(configPersistence, SOURCE_GITHUB);

    configPersistence.initialize(configs, SEED_PERSISTENCE);

    assertRecordCount(2);
    assertHasSource(SOURCE_GITHUB);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    verify(configPersistence, never()).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, times(1)).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  private void prepareLocalFilePersistence() throws Exception {
    Files.createDirectories(ROOT_PATH.resolve(FileSystemConfigPersistence.CONFIG_DIR));
    ConfigPersistence filePersistence = new FileSystemConfigPersistence(ROOT_PATH);
    writeSource(filePersistence, SOURCE_GITHUB);
    writeDestination(filePersistence, DESTINATION_S3);
  }

}
