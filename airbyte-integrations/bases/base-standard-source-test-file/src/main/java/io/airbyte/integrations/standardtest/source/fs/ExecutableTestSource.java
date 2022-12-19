/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.fs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.nio.file.Path;
import javax.annotation.Nullable;

/**
 * Extends TestSource such that it can be called using resources pulled from the file system. Will
 * also add the ability to execute arbitrary scripts in the next version.
 */
public class ExecutableTestSource extends SourceAcceptanceTest {

  public static class TestConfig {

    private final String imageName;
    private final Path specPath;
    private final Path configPath;
    private final Path catalogPath;

    private final Path statePath;

    public TestConfig(final String imageName, final Path specPath, final Path configPath, final Path catalogPath, final Path statePath) {
      this.imageName = imageName;
      this.specPath = specPath;
      this.configPath = configPath;
      this.catalogPath = catalogPath;
      this.statePath = statePath;
    }

    public String getImageName() {
      return imageName;
    }

    public Path getSpecPath() {
      return specPath;
    }

    public Path getConfigPath() {
      return configPath;
    }

    public Path getCatalogPath() {
      return catalogPath;
    }

    @Nullable
    public Path getStatePath() {
      return statePath;
    }

  }

  public static TestConfig TEST_CONFIG;

  @Override
  protected ConnectorSpecification getSpec() {
    return Jsons.deserialize(IOs.readFile(TEST_CONFIG.getSpecPath()), ConnectorSpecification.class);
  }

  @Override
  protected String getImageName() {
    return TEST_CONFIG.getImageName();
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.deserialize(IOs.readFile(TEST_CONFIG.getConfigPath()));
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return Jsons.deserialize(IOs.readFile(TEST_CONFIG.getCatalogPath()), ConfiguredAirbyteCatalog.class);
  }

  @Override
  protected JsonNode getState() {
    if (TEST_CONFIG.getStatePath() != null) {
      return Jsons.deserialize(IOs.readFile(TEST_CONFIG.getStatePath()));
    } else {
      return Jsons.deserialize("{}");
    }

  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    // no-op, for now
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    // no-op, for now
  }

}
