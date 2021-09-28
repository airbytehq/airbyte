/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.test_helpers;

import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.ProcessFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.util.Collections;

public class EntrypointEnvChecker {

  /**
   * @param processFactory any process factory
   * @param jobId used as input to processFactory.create
   * @param jobAttempt used as input to processFactory.create
   * @param jobRoot used as input to processFactory.create
   * @param imageName used as input to processFactory.create
   * @return the entrypoint in the env variable AIRBYTE_ENTRYPOINT
   * @throws RuntimeException if there is ambiguous output from the container
   */
  public static String getEntrypointEnvVariable(ProcessFactory processFactory, String jobId, int jobAttempt, Path jobRoot, String imageName)
      throws IOException, InterruptedException, WorkerException {
    Process process = processFactory.create(
        jobId,
        jobAttempt,
        jobRoot,
        imageName,
        false,
        Collections.emptyMap(),
        "printenv",
        WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS,
        Collections.emptyMap());

    BufferedReader stdout = new BufferedReader(new InputStreamReader(process.getInputStream()));

    String outputLine = null;

    String line = null;
    while (((line = stdout.readLine()) != null) && outputLine == null) {
      if (line.contains("AIRBYTE_ENTRYPOINT")) {
        outputLine = line;
      }
    }

    process.waitFor();

    if (outputLine != null) {
      String[] splits = outputLine.split("=", 2);
      if (splits.length != 2) {
        throw new RuntimeException("String could not be split into multiple segments: " + outputLine);
      } else {
        return splits[1].strip();
      }
    } else {
      return null;
    }
  }

}
