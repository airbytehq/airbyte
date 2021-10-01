/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
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
  protected List<String> getRegexTests() throws IOException {
    return Streams.stream(runExecutable(Command.GET_REGEX_TESTS).withArray("tests").elements())
        .map(JsonNode::textValue)
        .collect(toList());
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    testRoot = Files.createTempDirectory(Files.createDirectories(Path.of("/tmp/standard_test")), "pytest");
    runExecutableVoid(Command.SETUP);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
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

  private <T> T runExecutable(Command cmd, Class<T> klass) throws IOException {
    return Jsons.object(runExecutable(cmd), klass);
  }

  private JsonNode runExecutable(Command cmd) throws IOException {
    return Jsons.deserialize(IOs.readFile(runExecutableInternal(cmd), OUTPUT_FILENAME));
  }

  private void runExecutableVoid(Command cmd) throws IOException {
    runExecutableInternal(cmd);
  }

  private Path runExecutableInternal(Command cmd) throws IOException {
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

    int exitCode = process.exitValue();
    if (exitCode != 0) {
      throw new RuntimeException("python execution failed");
    }

    return testRoot;
  }

}
