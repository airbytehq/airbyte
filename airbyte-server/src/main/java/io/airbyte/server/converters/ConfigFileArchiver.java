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

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigFileArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigFileArchiver.class);
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";

  private final Path storageRoot;
  private final JsonSchemaValidator jsonSchemaValidator;

  public ConfigFileArchiver(final Path storageRoot, final JsonSchemaValidator jsonSchemaValidator) {
    this.storageRoot = storageRoot;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public ConfigFileArchiver(final Path storageRoot) {
    this(storageRoot, new JsonSchemaValidator());
  }

  private Path buildConfigPath(ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.toString()));
  }

  /**
   * Takes configuration objects from @param configList with schema @param schemaType and serializes
   * them into a single archive file stored in YAML. Objects will be ordered by their String
   * representation in the archive.
   */
  public <T> void writeConfigsToArchive(final ConfigSchema schemaType, final List<T> configList) throws IOException {
    final Path configPath = buildConfigPath(schemaType);
    Files.createDirectories(configPath.getParent());
    final List<T> sortedConfigs = configList.stream().sorted(Comparator.comparing(T::toString)).collect(Collectors.toList());
    Files.writeString(configPath, Yamls.serialize(sortedConfigs));
    LOGGER.debug(String.format("Successful export of airbyte config %s", schemaType));
  }

  /**
   * Reads a YAML configuration archive file and deserializes them into a list of configuration
   * objects. The objects will be validated against the current version of Airbyte server's JSON
   * Schema @param schemaType.
   */
  public <T> List<T> readConfigsFromArchive(final ConfigSchema schemaType, final Class<T> clazz) throws IOException, JsonValidationException {
    final List<T> results = new ArrayList<>();
    final Path configPath = buildConfigPath(schemaType);
    if (configPath.toFile().exists()) {
      final String configStr = Files.readString(configPath);
      final JsonNode node = Yamls.deserialize(configStr);
      final Iterator<JsonNode> it = node.elements();
      while (it.hasNext()) {
        final JsonNode element = it.next();
        final T config = Jsons.object(element, clazz);
        validateJson(config, schemaType);
        results.add(config);
      }
      LOGGER.debug(String.format("Successful read of airbyte config %s", schemaType));
    } else {
      LOGGER.debug(String.format("Airbyte config %s was not found", schemaType));
    }
    return results;
  }

  private <T> void validateJson(final T config, final ConfigSchema configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

}
