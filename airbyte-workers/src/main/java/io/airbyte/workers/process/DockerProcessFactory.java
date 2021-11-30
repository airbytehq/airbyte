/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Joiner;
import com.google.common.base.Strings;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerProcessFactory implements ProcessFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerProcessFactory.class);

  private static final Path DATA_MOUNT_DESTINATION = Path.of("/data");
  private static final Path LOCAL_MOUNT_DESTINATION = Path.of("/local");
  private static final String IMAGE_EXISTS_SCRIPT = "image_exists.sh";

  private final String workspaceMountSource;
  private final WorkerConfigs workerConfigs;
  private final Path workspaceRoot;
  private final String localMountSource;
  private final String networkName;
  private final boolean isOrchestrator;
  private final Path imageExistsScriptPath;

  /**
   * Used to construct a Docker process.
   *
   * @param workspaceRoot real root of workspace
   * @param workspaceMountSource workspace volume
   * @param localMountSource local volume
   * @param networkName docker network
   * @param isOrchestrator if the process needs to be able to launch containers
   */
  public DockerProcessFactory(final WorkerConfigs workerConfigs,
                              final Path workspaceRoot,
                              final String workspaceMountSource,
                              final String localMountSource,
                              final String networkName,
                              final boolean isOrchestrator) {
    this.workerConfigs = workerConfigs;
    this.workspaceRoot = workspaceRoot;
    this.workspaceMountSource = workspaceMountSource;
    this.localMountSource = localMountSource;
    this.networkName = networkName;
    this.isOrchestrator = isOrchestrator;
    this.imageExistsScriptPath = prepareImageExistsScript();
  }

  private static Path prepareImageExistsScript() {
    try {
      final Path basePath = Files.createTempDirectory("scripts");
      final String scriptContents = MoreResources.readResource(IMAGE_EXISTS_SCRIPT);
      final Path scriptPath = IOs.writeFile(basePath, IMAGE_EXISTS_SCRIPT, scriptContents);
      if (!scriptPath.toFile().setExecutable(true)) {
        throw new RuntimeException(String.format("Could not set %s to executable", scriptPath));
      }
      return scriptPath;
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public Process create(final String jobId,
                        final int attempt,
                        final Path jobRoot,
                        final String imageName,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final ResourceRequirements resourceRequirements,
                        final Map<String, String> labels,
                        final Map<Integer, Integer> internalToExternalPorts,
                        final String... args)
      throws WorkerException {
    try {
      if (!checkImageExists(imageName)) {
        throw new WorkerException("Could not find image: " + imageName);
      }

      if (!jobRoot.toFile().exists()) {
        Files.createDirectory(jobRoot);
      }

      for (final Map.Entry<String, String> file : files.entrySet()) {
        IOs.writeFile(jobRoot, file.getKey(), file.getValue());
      }

      List<String> cmd;

      // todo: add --expose 80 to each

      if (isOrchestrator) {
        cmd = Lists.newArrayList(
            "docker",
            "run",
            "--rm",
            "--init",
            "-i",
            "-v",
            String.format("%s:%s", workspaceMountSource, workspaceRoot), // real workspace root, not a rebased version
            "-v",
            String.format("%s:%s", localMountSource, LOCAL_MOUNT_DESTINATION),
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock", // needs to be able to run docker in docker
            "-w",
            jobRoot.toString(), // real jobroot, not rebased version
            "--network",
            networkName,
            "--log-driver",
            "none");
      } else {
        cmd = Lists.newArrayList(
            "docker",
            "run",
            "--rm",
            "--init",
            "-i",
            "-v",
            String.format("%s:%s", workspaceMountSource, DATA_MOUNT_DESTINATION), // uses job data mount
            "-v",
            String.format("%s:%s", localMountSource, LOCAL_MOUNT_DESTINATION),
            "-w",
            rebasePath(jobRoot).toString(), // rebases the job root on the job data mount
            "--network",
            networkName,
            "--log-driver",
            "none");
      }
      if (!Strings.isNullOrEmpty(entrypoint)) {
        cmd.add("--entrypoint");
        cmd.add(entrypoint);
      }
      if (resourceRequirements != null) {
        if (!Strings.isNullOrEmpty(resourceRequirements.getCpuRequest())) {
          cmd.add(String.format("--cpu-shares=%s", resourceRequirements.getCpuRequest()));
        }
        if (!Strings.isNullOrEmpty(resourceRequirements.getCpuLimit())) {
          cmd.add(String.format("--cpus=%s", resourceRequirements.getCpuLimit()));
        }
        if (!Strings.isNullOrEmpty(resourceRequirements.getMemoryRequest())) {
          cmd.add(String.format("--memory-reservation=%s", resourceRequirements.getMemoryRequest()));
        }
        if (!Strings.isNullOrEmpty(resourceRequirements.getMemoryLimit())) {
          cmd.add(String.format("--memory=%s", resourceRequirements.getMemoryLimit()));
        }
      }

      cmd.add(imageName);
      cmd.addAll(Arrays.asList(args));

      LOGGER.info("Preparing command: {}", Joiner.on(" ").join(cmd));

      return new ProcessBuilder(cmd).start();
    } catch (final IOException e) {
      throw new WorkerException(e.getMessage(), e);
    }
  }

  private Path rebasePath(final Path jobRoot) {
    final Path relativePath = workspaceRoot.relativize(jobRoot);
    return DATA_MOUNT_DESTINATION.resolve(relativePath);
  }

  @VisibleForTesting
  boolean checkImageExists(final String imageName) throws WorkerException {
    try {
      final Process process = new ProcessBuilder(imageExistsScriptPath.toString(), imageName).start();
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);
      LineGobbler.gobble(process.getInputStream(), LOGGER::info);

      WorkerUtils.gentleClose(workerConfigs, process, 10, TimeUnit.MINUTES);

      if (process.isAlive()) {
        throw new WorkerException("Process to check if image exists is stuck. Exiting.");
      } else {
        return process.exitValue() == 0;
      }
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

}
