/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Joiner;
import com.google.common.base.Strings;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerProcessFactory implements ProcessFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerProcessFactory.class);
  private static final int DOCKER_NAME_LEN_LIMIT = 128;

  private static final Path DATA_MOUNT_DESTINATION = Path.of("/data");
  private static final Path LOCAL_MOUNT_DESTINATION = Path.of("/local");
  private static final String IMAGE_EXISTS_SCRIPT = "image_exists.sh";

  private final String workspaceMountSource;
  private final WorkerConfigs workerConfigs;
  private final Path workspaceRoot;
  private final String localMountSource;
  private final String networkName;
  private final Path imageExistsScriptPath;

  /**
   * Used to construct a Docker process.
   *
   * @param workspaceRoot real root of workspace
   * @param workspaceMountSource workspace volume
   * @param localMountSource local volume
   * @param networkName docker network
   */
  public DockerProcessFactory(final WorkerConfigs workerConfigs,
                              final Path workspaceRoot,
                              final String workspaceMountSource,
                              final String localMountSource,
                              final String networkName) {
    this.workerConfigs = workerConfigs;
    this.workspaceRoot = workspaceRoot;
    this.workspaceMountSource = workspaceMountSource;
    this.localMountSource = localMountSource;
    this.networkName = networkName;
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
  public Process create(final String jobType,
                        final String jobId,
                        final int attempt,
                        final Path jobRoot,
                        final String imageName,
                        final boolean usesIsolatedPool,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final ResourceRequirements resourceRequirements,
                        final AllowedHosts allowedHosts,
                        final Map<String, String> labels,
                        final Map<String, String> jobMetadata,
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

      final List<String> cmd = Lists.newArrayList(
          "docker",
          "run",
          "--rm",
          "--init",
          "-i",
          "-w",
          rebasePath(jobRoot).toString(), // rebases the job root on the job data mount
          "--log-driver",
          "none");
      final String containerName = ProcessFactory.createProcessName(imageName, jobType, jobId, attempt, DOCKER_NAME_LEN_LIMIT);
      LOGGER.info("Creating docker container = {} with resources {} and allowedHosts {}", containerName, resourceRequirements, allowedHosts);
      cmd.add("--name");
      cmd.add(containerName);
      cmd.addAll(localDebuggingOptions(containerName));

      if (networkName != null) {
        cmd.add("--network");
        cmd.add(networkName);
      }

      if (workspaceMountSource != null) {
        cmd.add("-v");
        cmd.add(String.format("%s:%s", workspaceMountSource, DATA_MOUNT_DESTINATION));
      }

      if (localMountSource != null) {
        cmd.add("-v");
        cmd.add(String.format("%s:%s", localMountSource, LOCAL_MOUNT_DESTINATION));
      }

      final Map<String, String> allEnvMap = MoreMaps.merge(jobMetadata, workerConfigs.getEnvMap());
      for (final Map.Entry<String, String> envEntry : allEnvMap.entrySet()) {
        cmd.add("-e");
        cmd.add(envEntry.getKey() + "=" + envEntry.getValue());
      }

      if (!Strings.isNullOrEmpty(entrypoint)) {
        cmd.add("--entrypoint");
        cmd.add(entrypoint);
      }
      if (resourceRequirements != null) {
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

  /**
   * !! ONLY FOR DEBUGGING, SHOULD NOT BE USED IN PRODUCTION !! If you set the DEBUG_CONTAINER_IMAGE
   * environment variable, and it matches the image name of a spawned container, this method will add
   * the necessary params to connect a debugger. For example, to enable this for
   * `destination-bigquery` start the services locally with: ``` VERSION="dev"
   * DEBUG_CONTAINER_IMAGE="destination-bigquery" docker compose -f docker-compose.yaml -f
   * docker-compose.debug.yaml up ``` Additionally you may have to update the image version of your
   * target image to 'dev' in the UI of your local airbyte platform. See the
   * `docker-compose.debug.yaml` file for more context.
   *
   * @param containerName the name of the container which could be debugged.
   * @return A list with debugging arguments or an empty list
   */
  static List<String> localDebuggingOptions(final String containerName) {
    final boolean shouldAddDebuggerOptions =
        Optional.ofNullable(System.getenv("DEBUG_CONTAINER_IMAGE")).filter(StringUtils::isNotEmpty)
            .map(ProcessFactory.extractShortImageName(containerName)::equals).orElse(false)
            && Optional.ofNullable(System.getenv("DEBUG_CONTAINER_JAVA_OPTS")).isPresent();
    if (shouldAddDebuggerOptions) {
      return List.of("-e", "JAVA_TOOL_OPTIONS=" + System.getenv("DEBUG_CONTAINER_JAVA_OPTS"), "-p5005:5005");
    } else {
      return Collections.emptyList();
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

      WorkerUtils.gentleClose(process, 10, TimeUnit.MINUTES);

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
