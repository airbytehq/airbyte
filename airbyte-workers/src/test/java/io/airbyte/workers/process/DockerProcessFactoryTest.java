/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

// todo (cgardens) - these are not truly "unit" tests as they are check resources on the internet.
// we should move them to "integration" tests, when we have facility to do so.
class DockerProcessFactoryTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  /**
   * {@link DockerProcessFactoryTest#testImageExists()} will fail if jq is not installed. The logs get
   * swallowed when run from gradle. This test exists to explicitly fail with a clear error message
   * when jq is not installed.
   */
  @Test
  public void testJqExists() throws IOException {
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
  public void testImageExists() throws IOException, WorkerException {
    Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "process_factory");

    final DockerProcessFactory processFactory = new DockerProcessFactory(workspaceRoot, "", "", "");
    assertTrue(processFactory.checkImageExists("busybox"));
  }

  @Test
  public void testImageDoesNotExist() throws IOException, WorkerException {
    Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "process_factory");

    final DockerProcessFactory processFactory = new DockerProcessFactory(workspaceRoot, "", "", "");
    assertFalse(processFactory.checkImageExists("airbyte/fake:0.1.2"));
  }

  @Test
  public void testFileWriting() throws IOException, WorkerException {
    Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "process_factory");
    Path jobRoot = workspaceRoot.resolve("job");

    final DockerProcessFactory processFactory = new DockerProcessFactory(workspaceRoot, "", "", "");
    processFactory.create("job_id", 0, jobRoot, "busybox", false, ImmutableMap.of("config.json", "{\"data\": 2}"), "echo hi",
        WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS, Map.of());

    assertEquals(
        Jsons.jsonNode(ImmutableMap.of("data", 2)),
        Jsons.deserialize(IOs.readFile(jobRoot, "config.json")));
  }

}
