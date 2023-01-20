/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.google.common.base.Stopwatch;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

// todo (cgardens) - these are not truly "unit" tests as they are check resources on the internet.
// we should move them to "integration" tests, when we have facility to do so.
@Slf4j
class DockerProcessFactoryTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String PROCESS_FACTORY = "process_factory";
  private static final String BUSYBOX = "busybox";

  /**
   * {@link DockerProcessFactoryTest#testImageExists()} will fail if jq is not installed. The logs get
   * swallowed when run from gradle. This test exists to explicitly fail with a clear error message
   * when jq is not installed.
   */
  @Test
  void testJqExists() throws IOException {
    final Process process = new ProcessBuilder("jq", "--version").start();
    final StringBuilder out = new StringBuilder();
    final StringBuilder err = new StringBuilder();
    LineGobbler.gobble(process.getInputStream(), out::append);
    LineGobbler.gobble(process.getErrorStream(), err::append);

    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);

    assertEquals(0, process.exitValue(),
        String.format("Error while checking for jq. STDOUT: %s STDERR: %s Please make sure jq is installed (used by testImageExists)", out, err));
  }

  /**
   * This test will fail if jq is not installed. If run from gradle the log line that mentions the jq
   * issue will be swallowed. The exception is visible if run from intellij or with STDERR logging
   * turned on in gradle.
   */
  @Test
  void testImageExists() throws IOException, WorkerException {
    final Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), PROCESS_FACTORY);

    final DockerProcessFactory processFactory = new DockerProcessFactory(new WorkerConfigs(new EnvConfigs()), workspaceRoot, null, null, null);
    assertTrue(processFactory.checkImageExists(BUSYBOX));
  }

  @Test
  void testImageDoesNotExist() throws IOException, WorkerException {
    final Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), PROCESS_FACTORY);

    final DockerProcessFactory processFactory = new DockerProcessFactory(new WorkerConfigs(new EnvConfigs()), workspaceRoot, null, null, null);
    assertFalse(processFactory.checkImageExists("airbyte/fake:0.1.2"));
  }

  @Test
  void testFileWriting() throws IOException, WorkerException {
    final Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), PROCESS_FACTORY);
    final Path jobRoot = workspaceRoot.resolve("job");

    final DockerProcessFactory processFactory =
        new DockerProcessFactory(new WorkerConfigs(new EnvConfigs()), workspaceRoot, null, null, null);
    processFactory.create("tester", "job_id", 0, jobRoot, BUSYBOX, false, false, ImmutableMap.of("config.json", "{\"data\": 2}"), "echo hi",
        new WorkerConfigs(new EnvConfigs()).getResourceRequirements(), null, Map.of(), Map.of(), Map.of());

    assertEquals(
        Jsons.jsonNode(ImmutableMap.of("data", 2)),
        Jsons.deserialize(IOs.readFile(jobRoot, "config.json")));
  }

  /**
   * Tests that the env var map passed in is accessible within the process.
   */
  @Test
  void testEnvMapSet() throws IOException, WorkerException, InterruptedException {
    final Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), PROCESS_FACTORY);
    final Path jobRoot = workspaceRoot.resolve("job");

    final WorkerConfigs workerConfigs = spy(new WorkerConfigs(new EnvConfigs()));
    when(workerConfigs.getEnvMap()).thenReturn(Map.of("ENV_VAR_1", "ENV_VALUE_1"));

    final DockerProcessFactory processFactory =
        new DockerProcessFactory(
            workerConfigs,
            workspaceRoot,
            null,
            null,
            "host");

    waitForDockerToInitialize(processFactory, jobRoot, workerConfigs);

    final Process process = processFactory.create(
        "tester",
        "job_id",
        0,
        jobRoot,
        BUSYBOX,
        false,
        false,
        Map.of(),
        "/bin/sh",
        workerConfigs.getResourceRequirements(),
        null,
        Map.of(),
        Map.of(),
        Map.of(),
        "-c",
        "echo ENV_VAR_1=$ENV_VAR_1");

    final StringBuilder out = new StringBuilder();
    final StringBuilder err = new StringBuilder();
    LineGobbler.gobble(process.getInputStream(), out::append);
    LineGobbler.gobble(process.getErrorStream(), err::append);

    WorkerUtils.gentleClose(process, 20, TimeUnit.SECONDS);

    assertEquals(0, process.exitValue(), String.format("Process failed with stdout: %s and stderr: %s", out, err));
    assertEquals("ENV_VAR_1=ENV_VALUE_1", out.toString(), String.format("Output did not contain the expected string. stdout: %s", out));
  }

  private void waitForDockerToInitialize(final ProcessFactory processFactory, final Path jobRoot, final WorkerConfigs workerConfigs)
      throws InterruptedException, WorkerException {
    final var stopwatch = Stopwatch.createStarted();

    while (stopwatch.elapsed().compareTo(Duration.ofSeconds(30)) < 0) {
      final Process p = processFactory.create(
          "tester",
          "job_id_" + RandomStringUtils.randomAlphabetic(4),
          0,
          jobRoot,
          BUSYBOX,
          false,
          false,
          Map.of(),
          "/bin/sh",
          workerConfigs.getResourceRequirements(),
          null,
          Map.of(),
          Map.of(),
          Map.of(),
          "-c",
          "echo ENV_VAR_1=$ENV_VAR_1");
      p.waitFor();
      final int exitStatus = p.exitValue();

      if (exitStatus == 0) {
        log.info("Successfully ran test docker command.");
        return;
      }
    }

    throw new RuntimeException("Failed to run test docker command after timeout.");
  }

}
