/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.ProcessFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Collections;

/**
 * Should only be used by connector testing.
 */
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
  public static String getEntrypointEnvVariable(final ProcessFactory processFactory,
                                                final String jobId,
                                                final int jobAttempt,
                                                final Path jobRoot,
                                                final String imageName)
      throws IOException, InterruptedException, WorkerException {
    final Process process = processFactory.create(
        "entrypoint-checker",
        jobId,
        jobAttempt,
        jobRoot,
        imageName,
        false,
        Collections.emptyMap(),
        "printenv",
        null,
        Collections.emptyMap(),
        Collections.emptyMap(),
        Collections.emptyMap());

    final BufferedReader stdout = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));

    String outputLine = null;

    String line = stdout.readLine();
    while ((line != null) && outputLine == null) {
      if (line.contains("AIRBYTE_ENTRYPOINT")) {
        outputLine = line;
      }
      line = stdout.readLine();
    }

    process.waitFor();

    if (outputLine != null) {
      final String[] splits = outputLine.split("=", 2);
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
