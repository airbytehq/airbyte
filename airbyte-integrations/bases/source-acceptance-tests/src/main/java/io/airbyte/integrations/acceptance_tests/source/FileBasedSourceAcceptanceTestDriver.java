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

package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.integrations.acceptance_tests.source.core.CoreAcceptanceTest;
import io.airbyte.integrations.acceptance_tests.source.core.CoreAcceptanceTestRunner;
import io.airbyte.integrations.acceptance_tests.source.full_refresh.FullRefreshAcceptanceTestRunner;
import io.airbyte.integrations.acceptance_tests.source.incremental.IncrementalAcceptanceTestRunner;
import io.airbyte.integrations.acceptance_tests.source.models.CoreConfig;
import io.airbyte.integrations.acceptance_tests.source.models.FullRefreshConfig;
import io.airbyte.integrations.acceptance_tests.source.models.IncrementalConfig;
import io.airbyte.integrations.acceptance_tests.source.models.SourceAcceptanceTestInputs;
import io.airbyte.integrations.acceptance_tests.source.models.TestConfiguration;
import io.airbyte.integrations.acceptance_tests.source.utils.TestRunner;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class FileBasedSourceAcceptanceTestDriver {

  private static String readFileContents(String path) throws IOException {
    return Files.readString(Path.of(path));
  }

  private static JsonNode deserializeJsonAtPath(String path, String entity) {
    try {
      return Jsons.deserialize(readFileContents(path));
    } catch (Exception e) {
      throw new RuntimeException("Could not deserialize " + entity + " at path " + path, e);
    }
  }

  private static ConfiguredAirbyteCatalog deserializeConfiguredCatalogAtPath(String path) {
    return deserializeObjectAtPath(path, ConfiguredAirbyteCatalog.class, "configured catalog");
  }

  private static <T> T deserializeObjectAtPath(String path, Class<T> klass, String entity) {
    try {
      return Jsons.deserialize(readFileContents(path), klass);
    } catch (Exception e) {
      throw new RuntimeException("Could not deserialize " + entity + " at path " + path, e);
    }
  }

  List<Object> readTestInputs(SourceAcceptanceTestInputs testInputs) {
    Preconditions.checkNotNull(testInputs.getTests(), "Input test suite configurations cannot be empty or null.");
    Preconditions.checkArgument(testInputs.getTests().size() > 0, "Input test suite configurations cannot be empty or null.");
    List<Object> testConfigs = Lists.newArrayList();
    for (TestConfiguration testConfig : testInputs.getTests()) {
      Object config = switch (testConfig.getType()) {
        case CORE -> readCoreInputs(testInputs.getConnectorImage(), testConfig.getCore());
        case FULL_REFRESH -> readFullRefreshInputs(testInputs.getConnectorImage(), testConfig.getFullRefresh());
        case INCREMENTAL -> readIncrementalInputs(testInputs.getConnectorImage(), testConfig.getIncremental());
      };
      testConfigs.add(config);
    }
    return testConfigs;
  }

  IncrementalAcceptanceTestRunner.Config readIncrementalInputs(String connectorImage, IncrementalConfig config) {
    JsonNode connectorConfig = deserializeJsonAtPath(config.getConnectorConfigPath(), "connector config");
    var configuredCatalog = deserializeConfiguredCatalogAtPath(config.getConfiguredCatalogPath());
    return new IncrementalAcceptanceTestRunner.Config(connectorImage, connectorConfig, configuredCatalog);
  }

  FullRefreshAcceptanceTestRunner.Config readFullRefreshInputs(String connectorImage, FullRefreshConfig config) {
    JsonNode connectorConfig = deserializeJsonAtPath(config.getConnectorConfigPath(), "connector config");
    var configuredCatalog = deserializeConfiguredCatalogAtPath(config.getConfiguredCatalogPath());
    return new FullRefreshAcceptanceTestRunner.Config(connectorImage, connectorConfig, configuredCatalog);
  }

  CoreAcceptanceTestRunner.Config readCoreInputs(String connectorImage, CoreConfig coreConfig) {
    var catalog = deserializeConfiguredCatalogAtPath(coreConfig.getConfiguredCatalogPath());
    JsonNode expectedSpec = deserializeJsonAtPath(coreConfig.getSpecPath(), "specification");
    JsonNode validConnectorConfig = deserializeJsonAtPath(coreConfig.getValidConnectorConfigPath(), "valid connector config");
    JsonNode invalidConnectorConfig = deserializeJsonAtPath(coreConfig.getInvalidConnectorConfigPath(), "invalid connector config");

    return new CoreAcceptanceTestRunner.Config(connectorImage, expectedSpec, validConnectorConfig, invalidConnectorConfig, catalog);
  }

  private SourceAcceptanceTestInputs parseArguments(String[] args) throws IOException {
    ArgumentParser parser = ArgumentParsers.newFor(FileBasedSourceAcceptanceTestDriver.class.getName()).build()
        .defaultHelp(true)
        .description("Run source acceptance tests");

    parser.addArgument("--testConfig")
        .required(true)
        .help("Path to the source acceptance test input configuration");

    Namespace ns;
    try {
      ns = parser.parseArgs(args);
    } catch (ArgumentParserException e) {
      throw new IllegalArgumentException(e);
    }

    String testConfigPath = ns.getString("testConfig");
    String testConfig = Files.readString(Path.of(testConfigPath));
    return Yamls.deserialize(testConfig, SourceAcceptanceTestInputs.class);
  }

  void runTestSuite(String[] args) throws IOException {
    SourceAcceptanceTestInputs testInputs = parseArguments(args);
    List<Object> testConfigs = readTestInputs(testInputs);
    for (Object testConfig : testConfigs) {
      Class<?> klass = testConfig.getClass();

      if (klass == IncrementalAcceptanceTestRunner.Config.class) {
        IncrementalAcceptanceTestRunner.CONFIG = (IncrementalAcceptanceTestRunner.Config) testConfig;
        TestRunner.runTestClass(IncrementalAcceptanceTestRunner.class);
      } else if (klass == FullRefreshAcceptanceTestRunner.Config.class) {
        FullRefreshAcceptanceTestRunner.CONFIG = (FullRefreshAcceptanceTestRunner.Config) testConfig;
        TestRunner.runTestClass(FullRefreshAcceptanceTestRunner.class);
      } else if (klass == CoreAcceptanceTestRunner.Config.class) {
        CoreAcceptanceTestRunner.CONFIG = (CoreAcceptanceTestRunner.Config) testConfig;
        TestRunner.runTestClass(CoreAcceptanceTest.class);
      } else {
        throw new RuntimeException("Unrecognized test class " + klass);
      }
    }
  }

  public static void main(String[] args) throws IOException {
    new FileBasedSourceAcceptanceTestDriver().runTestSuite(args);
  }

}
