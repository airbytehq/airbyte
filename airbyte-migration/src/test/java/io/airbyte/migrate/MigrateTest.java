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

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.migrations.MigrationV0_11_0;
import io.airbyte.migrate.migrations.MigrationV0_11_0.ConfigKeys;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MigrateTest {

  private static final List<Migration> TEST_MIGRATIONS = Lists.newArrayList(new MigrationV0_11_0(), new MigrationV0_11_1());
  private Path migrateRoot;
  private Path inputRoot;
  private Path outputRoot;

  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final JsonNode STANDARD_SOURCE_DEFINITION1 = Jsons.jsonNode(ImmutableMap.builder()
      .put("sourceDefinitionId", UUID1)
      .put("name", "gold")
      .put("dockerRepository", "fort knox")
      .put("dockerImageTag", "latest")
      .put("documentationUrl", "airbyte.io")
      .build());
  private static final JsonNode STANDARD_SOURCE_DEFINITION2 = Jsons.jsonNode(ImmutableMap.builder()
      .put("sourceDefinitionId", UUID2)
      .put("name", "clones")
      .put("dockerRepository", "bank of karabraxos")
      .put("dockerImageTag", "v1.2.0")
      .put("documentationUrl", "airbyte.io")
      .build());
  private static final JsonNode AIRBYTE_METADATA = Jsons.jsonNode(ImmutableMap.of("key", "server_uuid", "value", UUID1));

  private static final Map<ResourceId, List<JsonNode>> V0_11_0_TEST_RECORDS = ImmutableMap
      .<ResourceId, List<JsonNode>>builder()
      .put(ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION"),
          ImmutableList.of(STANDARD_SOURCE_DEFINITION1, STANDARD_SOURCE_DEFINITION2))
      .put(ResourceId.fromConstantCase(ResourceType.JOB, "AIRBYTE_METADATA"), ImmutableList.of(AIRBYTE_METADATA))
      .build();

  @BeforeEach
  void setup() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "migration_test");
    migrateRoot = testRoot.resolve("migrate");
    inputRoot = testRoot.resolve("input");
    outputRoot = testRoot.resolve("output");
  }

  @Test
  void testMigrate() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(0).getVersion());
    final String targetVersion = TEST_MIGRATIONS.get(1).getVersion();

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);
    migrate.run(config);

    final Map<ResourceId, List<JsonNode>> expectedRecords = addFooBarToAllRecords(V0_11_0_TEST_RECORDS);
    assertExpectedOutputVersion(outputRoot, targetVersion);
    assertRecordsInOutput(ResourceType.CONFIG, Enums.valuesAsStrings(MigrationV0_11_0.ConfigKeys.class), expectedRecords);
    assertRecordsInOutput(ResourceType.JOB, Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class), expectedRecords);
  }

  @Test
  void testMultipleMigrations() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(0).getVersion());

    final List<Migration> migrations = ImmutableList.of(
        new MigrationV0_11_0(),
        createNoOpMigrationWithVersion("0.11.1"),
        createNoOpMigrationWithVersion("0.12.0"),
        createNoOpMigrationWithVersion("1.0.0"));

    final String targetVersion = migrations.get(3).getVersion();
    final Migrate migrate = new Migrate(migrateRoot, migrations);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);
    migrate.run(config);

    assertExpectedOutputVersion(outputRoot, targetVersion);
    assertRecordsInOutput(ResourceType.CONFIG, Enums.valuesAsStrings(MigrationV0_11_0.ConfigKeys.class), V0_11_0_TEST_RECORDS);
    assertRecordsInOutput(ResourceType.JOB, Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class), V0_11_0_TEST_RECORDS);
  }

  @Test
  void testInvalidInputRecord() throws IOException {
    // attempt to input records that have foobar added. the input schema does NOT include foobar.
    final Map<ResourceId, List<JsonNode>> invalidInputRecords = addFooBarToAllRecords(V0_11_0_TEST_RECORDS);
    writeInputArchive(inputRoot, invalidInputRecords, TEST_MIGRATIONS.get(0).getVersion());
    final String targetVersion = TEST_MIGRATIONS.get(1).getVersion();

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testInvalidOutputRecord() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(0).getVersion());

    // todo randomly generate?
    final String targetVersion = "v7";
    // use a migration that does not change the schema of the input, but has an output schema that
    // expects a change. (output schema expects foobar)
    final List<Migration> migrations =
        Lists.newArrayList(TEST_MIGRATIONS.get(0), createNoOpMigrationWithOutputSchema(targetVersion, TEST_MIGRATIONS.get(1).getOutputSchema()));

    final Migrate migrate = new Migrate(migrateRoot, migrations);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testMissingRecordResource() throws IOException {
    final Set<String> configResourcesMissingWorkspace = Enums.valuesAsStrings(ConfigKeys.class);
    configResourcesMissingWorkspace.remove(MigrationV0_11_0.ConfigKeys.STANDARD_WORKSPACE.name());
    writeInputs(
        ResourceType.CONFIG,
        configResourcesMissingWorkspace,
        inputRoot.resolve(ResourceType.CONFIG.getDirectoryName()),
        V0_11_0_TEST_RECORDS);
    writeInputs(
        ResourceType.CONFIG,
        Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class),
        inputRoot.resolve(ResourceType.JOB.getDirectoryName()),
        V0_11_0_TEST_RECORDS);
    IOs.writeFile(inputRoot, Migrate.VERSION_FILE_NAME, TEST_MIGRATIONS.get(0).getVersion());

    final String targetVersion = TEST_MIGRATIONS.get(1).getVersion();

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testMissingSchemaResource() throws IOException {
    final Set<String> configResourcesMissingWorkspace = Enums.valuesAsStrings(ConfigKeys.class);
    configResourcesMissingWorkspace.add("FAKE");
    writeInputs(
        ResourceType.CONFIG,
        configResourcesMissingWorkspace,
        inputRoot.resolve(ResourceType.CONFIG.getDirectoryName()),
        V0_11_0_TEST_RECORDS);
    writeInputs(
        ResourceType.JOB,
        Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class),
        inputRoot.resolve(ResourceType.JOB.getDirectoryName()),
        V0_11_0_TEST_RECORDS);
    IOs.writeFile(inputRoot, Migrate.VERSION_FILE_NAME, TEST_MIGRATIONS.get(0).getVersion());

    final String targetVersion = TEST_MIGRATIONS.get(1).getVersion();

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testInputVersionNotExists() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, "not a version");
    final String targetVersion = TEST_MIGRATIONS.get(1).getVersion();

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, targetVersion);

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testOutputVersionNotExists() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(0).getVersion());

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, "not a version");

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testCannotMigrateBackwards() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(1).getVersion());

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, TEST_MIGRATIONS.get(0).getVersion());

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  @Test
  void testCannotMigrateLaterally() throws IOException {
    writeInputArchive(inputRoot, V0_11_0_TEST_RECORDS, TEST_MIGRATIONS.get(0).getVersion());

    final Migrate migrate = new Migrate(migrateRoot, TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, TEST_MIGRATIONS.get(0).getVersion());

    assertThrows(IllegalArgumentException.class, () -> migrate.run(config));
  }

  private static void assertExpectedOutputVersion(Path outputRoot, String version) {
    final Path outputVersionFilePath = outputRoot.resolve(Migrate.VERSION_FILE_NAME);
    assertTrue(Files.exists(outputVersionFilePath));
    assertEquals(version, IOs.readFile(outputVersionFilePath));
  }

  private void assertRecordsInOutput(ResourceType resourceType,
                                     Set<String> resourceNames,
                                     Map<ResourceId, List<JsonNode>> expectedResourceIdToRecords) {
    resourceNames.forEach(resourceName -> {
      final ResourceId resourceId = ResourceId.fromConstantCase(resourceType, resourceName);
      final Path resourceFileOutputPath = outputRoot.resolve(resourceType.getDirectoryName()).resolve(resourceName + ".yaml");
      assertTrue(Files.exists(resourceFileOutputPath), "expected output file to exist: " + resourceFileOutputPath);
      final List<JsonNode> actualRecords = Jsons.children(Yamls.deserialize(IOs.readFile(resourceFileOutputPath)));
      final List<JsonNode> expectedRecords = expectedResourceIdToRecords.getOrDefault(resourceId, Collections.emptyList());

      assertEquals(expectedRecords, actualRecords, "Records did not match for resource: " + resourceId);
    });
  }

  private static Map<ResourceId, List<JsonNode>> addFooBarToAllRecords(Map<ResourceId, List<JsonNode>> records) {
    return records.entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> e.getValue()
            .stream()
            .map(r -> {
              final JsonNode expectedRecord = Jsons.clone(r);
              ((ObjectNode) expectedRecord).put("foo", "bar");
              return expectedRecord;
            })
            .collect(Collectors.toList())));
  }

  private static void writeInputs(ResourceType resourceType,
                                  Set<String> resourceNames,
                                  Path fileParent,
                                  Map<ResourceId, List<JsonNode>> resourceToRecords)
      throws IOException {
    Files.createDirectories(fileParent);
    resourceNames.forEach(resourceName -> {
      final ResourceId resourceId = ResourceId.fromConstantCase(resourceType, resourceName);
      final String records = Yamls.serialize(resourceToRecords.getOrDefault(resourceId, Collections.emptyList()));
      Exceptions.toRuntime(() -> Files.createDirectories(fileParent));
      IOs.writeFile(fileParent, resourceName + ".yaml", records);
    });
  }

  private static void writeInputArchive(Path archiveRoot, Map<ResourceId, List<JsonNode>> resourceToRecords, String version) throws IOException {
    writeInputs(
        ResourceType.CONFIG,
        Enums.valuesAsStrings(MigrationV0_11_0.ConfigKeys.class),
        archiveRoot.resolve(ResourceType.CONFIG.getDirectoryName()),
        resourceToRecords);
    writeInputs(
        ResourceType.JOB,
        Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class),
        archiveRoot.resolve(ResourceType.JOB.getDirectoryName()),
        resourceToRecords);
    IOs.writeFile(archiveRoot, Migrate.VERSION_FILE_NAME, version);
  }

  private static Migration createNoOpMigrationWithVersion(String version) {
    return new NoOpMigration(version, new MigrationV0_11_0().getOutputSchema(), new MigrationV0_11_0().getOutputSchema());
  }

  private static Migration createNoOpMigrationWithOutputSchema(String version, Map<ResourceId, JsonNode> outputSchema) {
    return new NoOpMigration(version, new MigrationV0_11_0().getOutputSchema(), outputSchema);
  }

  private static class NoOpMigration implements Migration {

    private final String version;
    private final Map<ResourceId, JsonNode> inputSchema;
    private final Map<ResourceId, JsonNode> outputSchema;

    public NoOpMigration(String version, Map<ResourceId, JsonNode> inputSchema, Map<ResourceId, JsonNode> outputSchema) {
      this.version = version;
      this.inputSchema = inputSchema;
      this.outputSchema = outputSchema;
    }

    @Override
    public String getVersion() {
      return version;
    }

    @Override
    public Map<ResourceId, JsonNode> getInputSchema() {
      return inputSchema;
    }

    @Override
    public Map<ResourceId, JsonNode> getOutputSchema() {
      return outputSchema;
    }

    @Override
    public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
      for (Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
        final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
        entry.getValue().forEach(recordConsumer);
      }
    }

  }

}
