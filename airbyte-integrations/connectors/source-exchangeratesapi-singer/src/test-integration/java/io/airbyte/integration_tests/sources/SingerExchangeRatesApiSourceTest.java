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

package io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SingerExchangeRatesApiSourceTest {

  private static final Path TESTS_PATH = Path.of("/tmp/airbyte_integration_tests");
  private static final String IMAGE_NAME = "airbyte/source-exchangeratesapi-singer-abprotocol:dev";

  private static final String CATALOG = "catalog.json";
  private static final String CONFIG = "config.json";

  protected Path jobRoot;
  protected Path workspaceRoot;
  AirbyteIntegrationLauncher launcher;
  protected Path catalogPath;

  @BeforeEach
  public void setUp() throws IOException {
    Files.createDirectories(TESTS_PATH);

    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "exchangeratesapi_io");
    jobRoot = workspaceRoot.resolve("job");
    catalogPath = jobRoot.resolve(CATALOG);

    Files.createDirectories(jobRoot);

    final ProcessBuilderFactory pbf = new DockerProcessBuilderFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        "",
        "host");

    launcher = new AirbyteIntegrationLauncher(IMAGE_NAME, pbf);
  }

  @Test
  public void testSpec() throws InterruptedException, IOException, WorkerException {
    Process process = createSpecProcess();
    process.waitFor();

    assertEquals(0, process.exitValue());

    // todo: add assertion to ensure the spec matches the schema / is serializable
  }

  @Test
  public void testCheck() throws IOException, WorkerException, InterruptedException {
    IOs.writeFile(jobRoot, CONFIG, "{}");

    Process process = createCheckProcess();
    process.waitFor();

    assertEquals(0, process.exitValue());
  }

  @Test
  public void testSuccessfulDiscover() throws IOException, InterruptedException, WorkerException {
    IOs.writeFile(jobRoot, CONFIG, "{}");

    Process process = createDiscoveryProcess();
    process.waitFor();

    assertEquals(0, process.exitValue());

    final String catalog = IOs.readFile(catalogPath);

    assertTrue(catalog.contains("USD"));
    assertTrue(catalog.contains("CHF"));
  }

  @Test
  public void testSync() throws IOException, InterruptedException, WorkerException {
    final Date date = Date.from(Instant.now().minus(3, ChronoUnit.DAYS));
    final SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd");

    IOs.writeFile(jobRoot, CONFIG, String.format("{\"start_date\":\"%s\"}", fmt.format(date)));
    IOs.writeFile(jobRoot, CATALOG, MoreResources.readResource("catalog.json"));

    final Path syncOutputPath = jobRoot.resolve("sync_output.txt");
    final Process process = createSyncProcess(syncOutputPath);
    process.waitFor();

    assertEquals(0, process.exitValue());

    final Optional<String> record = IOs.readFile(syncOutputPath).lines().filter(s -> s.contains("RECORD")).findFirst();
    assertTrue(record.isPresent(), "Date: " + date + "tap output: " + IOs.readFile(syncOutputPath));

    assertTrue(Jsons.deserialize(record.get())
        .get("record")
        .get("data")
        .get("CAD").asDouble() > 0);
  }

  private Process createSpecProcess() throws IOException, WorkerException {
    return launcher.spec(jobRoot)
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private Process createCheckProcess() throws IOException, WorkerException {
    return launcher.check(jobRoot, CONFIG)
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private Process createDiscoveryProcess() throws IOException, WorkerException {
    return launcher.discover(jobRoot, CONFIG)
        .redirectOutput(catalogPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private Process createSyncProcess(Path syncOutputPath) throws IOException, WorkerException {
    return launcher.read(jobRoot, CONFIG, "catalog.json")
        .redirectOutput(syncOutputPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

}
