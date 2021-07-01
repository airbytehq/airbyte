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
        WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

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
