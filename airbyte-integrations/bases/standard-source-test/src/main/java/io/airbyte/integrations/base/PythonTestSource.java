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

package io.airbyte.integrations.base;

import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
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
public class PythonTestSource extends TestSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(PythonTestSource.class);
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
  protected AirbyteCatalog getCatalog() throws IOException {
    return runExecutable(Command.GET_CATALOG, AirbyteCatalog.class);
  }

  @Override
  protected List<String> getRegexTests() throws IOException {
    return Streams.stream(runExecutable(Command.GET_REGEX_TESTS).withArray("tests").elements())
        .map(JsonNode::textValue)
        .collect(toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
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
    GET_CATALOG,
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
