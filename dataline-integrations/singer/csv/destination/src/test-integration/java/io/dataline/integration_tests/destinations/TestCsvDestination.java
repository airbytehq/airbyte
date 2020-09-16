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

package io.dataline.integration_tests.destinations;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertLinesMatch;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableMap;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.protocols.singer.SingerCheckConnectionWorker;
import io.dataline.workers.protocols.singer.SingerDiscoverSchemaWorker;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("ResultOfMethodCallIgnored")
class TestCsvDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestCsvDestination.class);

  private static final String IMAGE_NAME = "dataline/integration-singer-csv-destination:dev";
  private static final Path TESTS_PATH = Path.of("/tmp/dataline_integration_tests");
  private static final List<String> EXPECTED_OUTPUT =
      Arrays.asList(("date,NZD,HKD\n" +
          "2020-08-29T00:00:00Z,0.12,2.13\n" +
          "2020-08-30T00:00:00Z,1.14,7.15\n" +
          "2020-08-31T00:00:00Z,1.14,7.15,10.16\n" +
          "2020-08-31T00:00:00Z,1.99,7.99,10.99\n" +
          "2020-09-01T00:00:00Z,1.14,7.15,10.16").split("\n"));

  protected Path jobRoot;
  protected Path workspaceRoot;
  protected Path localRoot;
  protected ProcessBuilderFactory pbf;

  private Process process;

  @BeforeEach
  public void setUp() throws IOException {
    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "dataline-integration");
    localRoot = Files.createTempDirectory(TESTS_PATH, "dataline-local");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), localRoot.toString(), "host");

    LOGGER.debug("workspaceRoot - {}", workspaceRoot);
    LOGGER.debug("localRoot - {}", localRoot);
  }

  @AfterEach
  public void tearDown() {
    WorkerUtils.closeProcess(process);
  }

  private static Path removeLeadingSlash(Path path) {
    return Path.of(path.toString().replaceAll("^/+", ""));
  }

  @Test
  public void testWithRelativePath() throws IOException, InterruptedException {
    final Path destinationPath = Path.of("users");

    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    Path javaDestinationPath = localRoot.resolve(destinationPath);
    javaDestinationPath.toFile().mkdirs();
    assertProducesExpectedOutput(config, javaDestinationPath);
  }

  // todo (cgardens) - if a user inputs a leading slash, we do not treat it like an absolute path,
  // but instead try to use it as a relative path, relative the localRoot. we test this here,
  // since we do not have a good way to validate this at the time of configuration.
  @Test
  public void testWithAbsolutePath() throws IOException, InterruptedException {
    final Path destinationPath = Path.of("/users");
    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    Path javaDestinationPath = localRoot.resolve(removeLeadingSlash(destinationPath));
    javaDestinationPath.toFile().mkdirs();

    assertProducesExpectedOutput(config, javaDestinationPath);
  }

  @Test
  public void testNoPath() throws IOException, InterruptedException {
    final Path destinationPath = Path.of("");
    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    Path javaDestinationPath = localRoot.resolve(destinationPath);
    javaDestinationPath.toFile().mkdirs();

    assertProducesExpectedOutput(config, javaDestinationPath);
  }

  // todo (cgarens) - part of the contract is that the path you put in, better already exist on
  // your local filesystem. this contract is a sideffect of how the singer target-csv lib is
  // implemented. in the future, we'd likely want our version of this to be able to create
  // any directories necessary within the local root.
  @Test
  public void testWithRelativePathThatDoesNotExist() throws IOException, InterruptedException {
    final Path destinationPath = Path.of("users");
    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    Path javaDestinationPath = localRoot.resolve(destinationPath);

    assertThrows(Exception.class, () -> assertProducesExpectedOutput(config, javaDestinationPath));
  }

  @Test
  public void testConnectionSuccessful() throws InvalidCredentialsException, InvalidCatalogException {
    final Path destinationPath = Path.of("users");
    Path javaDestinationPath = localRoot.resolve(destinationPath);
    javaDestinationPath.toFile().mkdirs();

    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    SingerCheckConnectionWorker checkConnectionWorker = new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(config));
    OutputAndStatus<StandardCheckConnectionOutput> run = checkConnectionWorker.run(inputConfig, jobRoot);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, run.getOutput().get().getStatus());
  }

  @Test
  public void testConnectionUnsuccessful() throws InvalidCredentialsException, InvalidCatalogException {
    final Path destinationPath = Path.of("users");

    final Map<String, Object> config = createConfigWithDestinationPath(destinationPath);
    SingerCheckConnectionWorker checkConnectionWorker = new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(config));
    OutputAndStatus<StandardCheckConnectionOutput> run = checkConnectionWorker.run(inputConfig, jobRoot);
    assertEquals(JobStatus.FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, run.getOutput().get().getStatus());
  }

  private void assertProducesExpectedOutput(Map<String, Object> config, Path outputPathOnLocalFs) throws IOException, InterruptedException {
    writeConfigFileToJobRoot(Jsons.serialize(config));
    process = startTarget();

    writeResourceToStdIn("singer-tap-output.txt", process);
    process.getOutputStream().close();

    process.waitFor();

    List<String> actualList = getOutput(outputPathOnLocalFs);
    assertLinesMatch(EXPECTED_OUTPUT, actualList);
  }

  private Process startTarget() throws IOException {
    return pbf.create(jobRoot, IMAGE_NAME, "--config", WorkerConstants.TARGET_CONFIG_JSON_FILENAME)
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private void writeConfigFileToJobRoot(String fileContent) throws IOException {
    Files.writeString(Path.of(jobRoot.toString(), WorkerConstants.TARGET_CONFIG_JSON_FILENAME), fileContent);
  }

  private void writeResourceToStdIn(String resourceName, Process process) throws IOException {
    Objects.requireNonNull(getClass().getClassLoader().getResourceAsStream(resourceName))
        .transferTo(process.getOutputStream());
  }

  private List<String> getOutput(Path destinationPath) throws IOException {
    final List<Path> files = Files.list(destinationPath).collect(Collectors.toList());
    assertEquals(1, files.size());

    return Files.readAllLines(files.get(0), StandardCharsets.UTF_8);
  }

  private static Map<String, Object> createConfigWithDestinationPath(Path destinationPath) {
    return ImmutableMap.<String, Object>builder()
        .put("delimeter", ",")
        .put("quotechar", '"')
        .put("destination_path", destinationPath.toString())
        .build();

  }

}
