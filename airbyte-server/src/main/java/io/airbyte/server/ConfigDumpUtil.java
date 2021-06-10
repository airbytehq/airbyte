package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class ConfigDumpUtil {

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
