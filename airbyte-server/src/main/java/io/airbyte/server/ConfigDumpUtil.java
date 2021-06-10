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

package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigDumpUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigDumpUtil.class);
  private final Path storageRoot;

  private static final String CONFIG_DIR = "config";

  public ConfigDumpUtil(Path storageRoot) {
    this.storageRoot = storageRoot.resolve(CONFIG_DIR);
  }

  public List<String> listDirectories() throws IOException {
    try (Stream<Path> files = Files.list(storageRoot)) {
      List<String> directoryName = files.map(c -> c.getFileName().toString())
          .collect(Collectors.toList());
      return directoryName;

    }
  }

  public void orphanDirectories() throws IOException {
    Set<String> configSchemas = Arrays.asList(ConfigSchema.values()).stream().map(c -> c.toString())
        .collect(
            Collectors.toSet());
    for (String directory : listDirectories()) {
      if (!configSchemas.contains(directory)) {
        File file = storageRoot.resolve(directory).toFile();
        LOGGER.info("Deleting directory " + file);
        if (!FileUtils.deleteQuietly(file)) {
          LOGGER.warn("Could not delete directory " + file);
        }
      }
    }
  }

  public List<JsonNode> listConfig(String configType) throws IOException {
    final Path configTypePath = storageRoot.resolve(configType);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }
    try (Stream<Path> files = Files.list(configTypePath)) {
      final List<String> ids = files
          .filter(p -> !p.endsWith(".json"))
          .map(p -> p.getFileName().toString().replace(".json", ""))
          .collect(Collectors.toList());

      final List<JsonNode> configs = Lists.newArrayList();
      for (String id : ids) {
        try {
          final Path configPath = storageRoot.resolve(configType).resolve(String.format("%s.json", id));
          if (!Files.exists(configPath)) {
            throw new RuntimeException("Config NotFound");
          }

          final JsonNode config = Jsons.deserialize(Files.readString(configPath), JsonNode.class);
          configs.add(config);
        } catch (RuntimeException e) {
          throw new IOException(e);
        }
      }

      return configs;
    }
  }

}
