/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardSource;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultConfigPersistenceTest {

  private Path rootPath;
  private DefaultConfigPersistence configPersistence;

  @BeforeEach
  void setUp() throws IOException {
    rootPath = Files.createTempDirectory(DefaultConfigPersistenceTest.class.getName());
    configPersistence = new DefaultConfigPersistence(rootPath);
  }

  private StandardSource generateStandardSource() {
    final UUID sourceId = UUID.randomUUID();

    final StandardSource standardSource = new StandardSource();
    standardSource.setSourceId(sourceId);
    standardSource.setName("apache storm");

    return standardSource;
  }

  private JsonNode generateStandardSourceJson(UUID sourceId) {
    return Jsons.jsonNode(ImmutableMap.of("sourceId", sourceId.toString(), "name", "apache storm"));
  }

  @Test
  void getConfig() throws IOException, JsonValidationException, ConfigNotFoundException {
    StandardSource standardSource = generateStandardSource();
    JsonNode expectedJson = generateStandardSourceJson(standardSource.getSourceId());

    // manually write json to disk.
    final Path standardSourceDir = rootPath.resolve("STANDARD_SOURCE");
    FileUtils.forceMkdir(standardSourceDir.toFile());
    Path configPath = standardSourceDir.resolve(standardSource.getSourceId().toString() + ".json");
    Files.writeString(configPath, expectedJson.toString());

    final StandardSource actualSource =
        configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SOURCE,
            standardSource.getSourceId().toString(),
            StandardSource.class);

    assertEquals(standardSource, actualSource);
  }

  @Test
  void getConfigs() throws JsonValidationException, IOException {
    StandardSource standardSource = generateStandardSource();
    JsonNode expectedJson = generateStandardSourceJson(standardSource.getSourceId());

    // manually write json to disk.
    final Path standardSourceDir = rootPath.resolve("STANDARD_SOURCE");
    FileUtils.forceMkdir(standardSourceDir.toFile());
    Path configPath = standardSourceDir.resolve(standardSource.getSourceId().toString() + ".json");
    Files.writeString(configPath, expectedJson.toString());

    final Set<StandardSource> actualSource =
        configPersistence.getConfigs(PersistenceConfigType.STANDARD_SOURCE, StandardSource.class);

    assertEquals(standardSource, actualSource.iterator().next());
  }

  @Test
  void writeConfig() throws JsonValidationException, IOException {
    StandardSource standardSource = generateStandardSource();
    JsonNode expectedJson = generateStandardSourceJson(standardSource.getSourceId());

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SOURCE,
        standardSource.getSourceId().toString(),
        standardSource);

    final Path expectedPath =
        rootPath
            .resolve("STANDARD_SOURCE")
            .resolve(standardSource.getSourceId().toString() + ".json");

    // check reading to pojo
    final StandardSource actualSource =
        Jsons.deserialize(Files.readString(expectedPath), StandardSource.class);
    assertEquals(standardSource, actualSource);

    // check reading to json
    final JsonNode actualJson = Jsons.deserialize(Files.readString(expectedPath));
    assertEquals(expectedJson, actualJson);
  }

  @Test
  void writeConfigInvalidConfig() {
    StandardSource standardSource = generateStandardSource();
    standardSource.setName(null);

    try {
      configPersistence.writeConfig(
          PersistenceConfigType.STANDARD_SOURCE,
          standardSource.getSourceId().toString(),
          standardSource);
    } catch (JsonValidationException e) {
      return;
    }
    fail("expected to throw invalid json exception.");
  }

}
