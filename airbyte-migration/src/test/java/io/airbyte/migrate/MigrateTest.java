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
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.migrations.MigrationV0_11_0;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MigrateTest {

  private static final List<Migration> TEST_MIGRATIONS = Lists.newArrayList(new MigrationV0_11_0(), new MigrationV0_11_1());
  private Path migrateRoot;
  private Path inputRoot;
  private Path outputRoot;

  @BeforeEach
  void setup() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "test");
    migrateRoot = testRoot.resolve("migrate");
    inputRoot = testRoot.resolve("input");
    outputRoot = testRoot.resolve("output");
  }

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
  private static final JsonNode AIRBYTE_METADATA = Jsons.jsonNode(ImmutableMap.of("server_uuid", UUID1));

  @Test
  void testMigrate() throws IOException {
    final Map<ResourceId, List<JsonNode>> resourceToRecords = ImmutableMap
        .<ResourceId, List<JsonNode>>builder()
        .put(ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION"),
            ImmutableList.of(STANDARD_SOURCE_DEFINITION1, STANDARD_SOURCE_DEFINITION2))
        .put(ResourceId.fromConstantCase(ResourceType.JOB, "AIRBYTE_METADATA"), ImmutableList.of(AIRBYTE_METADATA))
        .build();

    writeInputArchive(inputRoot, resourceToRecords, TEST_MIGRATIONS.get(0).getVersion());

    final Migrate migrate = new Migrate(migrateRoot, new JsonSchemaValidator(), TEST_MIGRATIONS);
    final MigrateConfig config = new MigrateConfig(inputRoot, outputRoot, TEST_MIGRATIONS.get(1).getVersion());
    migrate.run(config);

    Arrays.stream(MigrationV0_11_0.ConfigKeys.values()).forEach(resourceName -> {
      final ResourceId resourceId = ResourceId.fromConstantCase(ResourceType.CONFIG, resourceName.toString());
      final Path resourceFileOutputPath = outputRoot.resolve("config").resolve(resourceName.toString() + ".yaml");
      assertTrue(Files.exists(resourceFileOutputPath));
      final List<JsonNode> actualRecords = MoreStreams
          .toStream(Yamls.deserialize(IOs.readFile(resourceFileOutputPath)).elements()).collect(Collectors.toList());

      final List<JsonNode> expectedRecords = resourceToRecords.getOrDefault(resourceId, Collections.emptyList())
          .stream()
          .map(r -> {
            final JsonNode expectedRecord = Jsons.clone(r);
            ((ObjectNode) expectedRecord).put("foo", "bar");
            return expectedRecord;
          })
          .collect(Collectors.toList());

      assertEquals(expectedRecords, actualRecords);

    });
  }

  private static void writeInputs(Set<String> resourceNames, Path fileParent, Map<ResourceId, List<JsonNode>> resourceToRecords) throws IOException {
    Files.createDirectories(fileParent);
    resourceNames.forEach(resourceName -> {
      final ResourceId resourceId = ResourceId.fromConstantCase(ResourceType.CONFIG, resourceName);
      final String records = Yamls.serialize(resourceToRecords.getOrDefault(resourceId, Collections.emptyList()));
      Exceptions.toRuntime(() -> Files.createDirectories(fileParent));
      IOs.writeFile(fileParent, resourceName + ".yaml", records);
    });
  }

  private static void writeInputArchive(Path archiveRoot, Map<ResourceId, List<JsonNode>> resourceToRecords, String version) throws IOException {
    writeInputs(Enums.valuesAsStrings(MigrationV0_11_0.ConfigKeys.class), archiveRoot.resolve(ResourceType.CONFIG.getDirectoryName()),
        resourceToRecords);
    writeInputs(Enums.valuesAsStrings(MigrationV0_11_0.JobKeys.class), archiveRoot.resolve(ResourceType.JOB.getDirectoryName()), resourceToRecords);
    IOs.writeFile(archiveRoot, Migrate.VERSION_FILE_NAME, version);
  }

}
