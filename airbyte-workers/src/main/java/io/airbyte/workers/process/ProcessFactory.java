/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public interface ProcessFactory {

  /**
   * Creates a ProcessBuilder to run a program in a new Process.
   *
   * @param jobId job Id
   * @param attempt attempt Id
   * @param jobPath Workspace directory to run the process from.
   * @param imageName Docker image name to start the process from.
   * @param files File name to contents map that will be written into the working dir of the process
   *        prior to execution.
   * @param entrypoint If not null, the default entrypoint program of the docker image can be changed
   *        by this argument.
   * @param resourceRequirements CPU and RAM to assign to the created process.
   * @param labels Labels to assign to the created Kube pod, if any. Ignore for docker.
   * @param args Arguments to pass to the docker image being run in the new process.
   * @return ProcessBuilder object to run the process.
   * @throws WorkerException
   */
  Process create(String jobId,
                 int attempt,
                 final Path jobPath,
                 final String imageName,
                 final boolean usesStdin,
                 final Map<String, String> files,
                 final String entrypoint,
                 final ResourceRequirements resourceRequirements,
                 final Map<String, String> labels,
                 final String... args)
      throws WorkerException;

  default Process create(String jobId,
                         int attempt,
                         final Path jobPath,
                         final String imageName,
                         final boolean usesStdin,
                         final Map<String, String> files,
                         final String entrypoint,
                         final ResourceRequirements resourceRequirements,
                         final Map<String, String> labels,
                         final List<String> args)
      throws WorkerException {
    return create(jobId, attempt, jobPath, imageName, usesStdin, files, entrypoint, resourceRequirements, labels, args.toArray(new String[0]));
  }

}
