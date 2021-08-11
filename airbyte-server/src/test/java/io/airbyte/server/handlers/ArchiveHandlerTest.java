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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.YamlSeedConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.File;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class ArchiveHandlerTest {

  private static final String VERSION = "0.6.8";
  private static PostgreSQLContainer<?> container;

  private Database database;
  private JobPersistence jobPersistence;
  private ConfigPersistence configPersistence;
  private ConfigPersistence seedPersistence;

  private ConfigRepository configRepository;
  private ArchiveHandler archiveHandler;

  private static class NoOpFileTtlManager extends FileTtlManager {

    public NoOpFileTtlManager() {
      super(1L, TimeUnit.MINUTES, 1L);
    }

    public void register(Path path) {}

  }

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @BeforeEach
  public void setup() throws Exception {
    database = new JobsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    jobPersistence = new DefaultJobPersistence(database);
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    seedPersistence = YamlSeedConfigPersistence.get();
    configPersistence = new DatabaseConfigPersistence(database).loadData(seedPersistence);
    configRepository = new ConfigRepository(configPersistence);

    jobPersistence.setVersion(VERSION);

    archiveHandler = new ArchiveHandler(
        VERSION,
        configRepository,
        jobPersistence,
        new NoOpFileTtlManager());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  /**
   * After exporting and importing, the configs should remain the same.
   */
  @Test
  void testRoundTrip() throws Exception {
    assertSameConfigDump(seedPersistence.dumpConfigs(), configRepository.dumpConfigs());

    // Export the configs.
    File archive = archiveHandler.exportData();

    // After deleting the configs, the dump becomes empty.
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    assertSameConfigDump(Collections.emptyMap(), configRepository.dumpConfigs());

    // After importing the configs, the dump is restored.
    ImportRead importResult = archiveHandler.importData(archive);
    assertEquals(StatusEnum.SUCCEEDED, importResult.getStatus());
    assertSameConfigDump(seedPersistence.dumpConfigs(), configRepository.dumpConfigs());

    // When a connector definition is in use, it will not be updated.
    UUID sourceS3DefinitionId = UUID.fromString("69589781-7828-43c5-9f63-8925b1c1ccc2");
    String sourceS3DefinitionVersion = "0.0.0";
    StandardSourceDefinition sourceS3Definition = seedPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceS3DefinitionId.toString(),
        StandardSourceDefinition.class)
        // This source definition is on an old version
        .withDockerImageTag(sourceS3DefinitionVersion);
    SourceConnection sourceConnection = new SourceConnection()
        .withSourceDefinitionId(sourceS3DefinitionId)
        .withSourceId(UUID.randomUUID())
        .withWorkspaceId(UUID.randomUUID())
        .withName("Test source")
        .withConfiguration(Jsons.deserialize("{}"))
        .withTombstone(false);

    // Write source connection and an old source definition.
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, sourceConnection.getSourceId().toString(), sourceConnection);
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceS3DefinitionId.toString(), sourceS3Definition);

    // Export, wipe, and import the configs.
    archive = archiveHandler.exportData();
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    archiveHandler.importData(archive);

    // The version has not changed.
    StandardSourceDefinition actualS3Definition = configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceS3DefinitionId.toString(),
        StandardSourceDefinition.class);
    assertEquals(sourceS3DefinitionVersion, actualS3Definition.getDockerImageTag());
  }

  private Map<String, Set<JsonNode>> getSetFromStream(Map<String, Stream<JsonNode>> input) {
    return input.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().collect(Collectors.toSet())));
  }

  // assertEquals cannot correctly check the equality of two maps with stream values,
  // so streams are converted to sets before being compared.
  private void assertSameConfigDump(Map<String, Stream<JsonNode>> expected, Map<String, Stream<JsonNode>> actual) {
    assertEquals(getSetFromStream(expected), getSetFromStream(actual));
  }

}
