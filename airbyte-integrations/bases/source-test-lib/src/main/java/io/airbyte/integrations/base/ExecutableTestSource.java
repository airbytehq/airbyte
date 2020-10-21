package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import java.nio.file.Path;

/**
 * Extends TestSource such that it can be called using resources pulled from the file system. Will also add the ability to execute arbitrary scripts in the next version.
 */
public class ExecutableTestSource extends TestSource {
  public static class TestConfig {

    private final String imageName;
    private final Path configPath;
    private final Path catalogPath;

    public TestConfig(String imageName, Path configPath, Path catalogPath) {
      this.imageName = imageName;
      this.configPath = configPath;
      this.catalogPath = catalogPath;
    }

    public Path getConfigPath() {
      return configPath;
    }

    public Path getCatalogPath() {
      return catalogPath;
    }

    public String getImageName() {
      return imageName;
    }
  }

  public static TestConfig TEST_CONFIG;

  @Override
  protected String getImageName() {
    return TEST_CONFIG.getImageName();
  }

  @Override
  protected JsonNode getConfig() {
    final JsonNode deserialize = Jsons.deserialize(IOs.readFile(TEST_CONFIG.getConfigPath()));
    System.out.println("deserialize = " + deserialize);
    return deserialize;
  }

  @Override
  protected AirbyteCatalog getCatalog() {
    final AirbyteCatalog catalog = Jsons.deserialize(IOs.readFile(TEST_CONFIG.getCatalogPath()), AirbyteCatalog.class);
    System.out.println("catalog = " + Jsons.serialize(catalog));
    return catalog;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    // no-op, for now
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    // no-op, for now
  }
}
