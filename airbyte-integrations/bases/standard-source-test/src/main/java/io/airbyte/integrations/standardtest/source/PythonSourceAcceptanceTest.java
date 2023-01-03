/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Extends TestSource such that it can be called using resources pulled from the file system. Will
 * also add the ability to execute arbitrary scripts in the next version.
 */
public class PythonSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(PythonSourceAcceptanceTest.class);
  private static final String OUTPUT_FILENAME = "output.json";

  public static String IMAGE_NAME;
  public static String PYTHON_CONTAINER_NAME;

  private Path testRoot;

  @Override
  protected String getImageName() {
    return IMAGE_NAME;
  }

  @Override
  protected ConnectorSpecification getSpec() throws IOException {
    return runExecutable(Command.GET_SPEC, ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() throws IOException {
    return runExecutable(Command.GET_CONFIG);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws IOException {
    return runExecutable(Command.GET_CONFIGURED_CATALOG, ConfiguredAirbyteCatalog.class);
  }

  @Override
  protected JsonNode getState() throws IOException {
    return runExecutable(Command.GET_STATE);
  }

  @Override
  protected void assertFullRefreshMessages(final List<AirbyteMessage> allMessages) throws IOException {
    final List<String> regexTests = Streams.stream(runExecutable(Command.GET_REGEX_TESTS).withArray("tests").elements())
        .map(JsonNode::textValue).toList();
    final List<String> stringMessages = allMessages.stream().map(Jsons::serialize).toList();
    LOGGER.info("Running " + regexTests.size() + " regex tests...");
    regexTests.forEach(regex -> {
      LOGGER.info("Looking for [" + regex + "]");
      assertTrue(stringMessages.stream().anyMatch(line -> line.matches(regex)), "Failed to find regex: " + regex);
    });
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testRoot = Files.createTempDirectory(Files.createDirectories(Path.of("/tmp/standard_test")), "pytest");
    runExecutableVoid(Command.SETUP);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    runExecutableVoid(Command.TEARDOWN);
  }

  private enum Command {
    GET_SPEC,
    GET_CONFIG,
    GET_CONFIGURED_CATALOG,
    GET_STATE,
    GET_REGEX_TESTS,
    SETUP,
    TEARDOWN
  }

  private <T> T runExecutable(final Command cmd, final Class<T> klass) throws IOException {
    return Jsons.object(runExecutable(cmd), klass);
  }

  private JsonNode runExecutable(final Command cmd) throws IOException {
    return Jsons.deserialize(IOs.readFile(runExecutableInternal(cmd), OUTPUT_FILENAME));
  }

  private void runExecutableVoid(final Command cmd) throws IOException {
    runExecutableInternal(cmd);
  }

  private Path runExecutableInternal(final Command cmd) throws IOException {
    LOGGER.info("testRoot = " + testRoot);
    final List<String> dockerCmd =
        Lists.newArrayList(
            "docker",
            "run",
            "--rm",
            "-i",
            "-v",
            String.format("%s:%s", testRoot, "/test_root"),
            "-w",
            testRoot.toString(),
            "--network",
            "host",
            PYTHON_CONTAINER_NAME,
            cmd.toString().toLowerCase(),
            "--out",
            "/test_root");

    final Process process = new ProcessBuilder(dockerCmd).start();
    LineGobbler.gobble(process.getErrorStream(), LOGGER::error);
    LineGobbler.gobble(process.getInputStream(), LOGGER::info);

    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);

    final int exitCode = process.exitValue();
    if (exitCode != 0) {
      throw new RuntimeException("python execution failed");
    }

    return testRoot;
  }

}
