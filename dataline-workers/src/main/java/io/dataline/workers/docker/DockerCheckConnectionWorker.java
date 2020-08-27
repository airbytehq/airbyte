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

package io.dataline.workers.docker;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.utils.DockerUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerCheckConnectionWorker implements CheckConnectionWorker {
  private static final Logger LOGGER = LoggerFactory.getLogger(DockerCheckConnectionWorker.class);

  private static final String INPUT = "input.json";
  private static final String OUTPUT = "output.json";

  private final String imageName;

  Process tapProcess;

  public DockerCheckConnectionWorker(String imageName) {
    this.imageName = imageName;
  }

  @Override
  public OutputAndStatus<StandardCheckConnectionOutput> run(
      StandardCheckConnectionInput standardCheckConnectionInput, Path workspacePath) {
    final ObjectMapper objectMapper = new ObjectMapper();

    // mount input struct to known location on docker container.
    final Path configPath =
        WorkerUtils.writeObjectToJsonFileWorkspace(
            workspacePath, INPUT, standardCheckConnectionInput);

    // run it.
    try {
      String[] cmd =
          DockerUtils.getDockerCommand(workspacePath, imageName, "--config", configPath.toString());

      LOGGER.debug("Command: {}", String.join(" ", cmd));

      tapProcess = new ProcessBuilder().command(cmd).start();

      while (!tapProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug("Waiting for worker");
      }

      // read output struct from known location on docker container.
      final StandardCheckConnectionOutput standardCheckConnectionOutput =
          WorkerUtils.readObjectFromJsonFileWorkspace(
              workspacePath, OUTPUT, StandardCheckConnectionOutput.class);

      return new OutputAndStatus<>(JobStatus.SUCCESSFUL, standardCheckConnectionOutput);
    } catch (IOException | InterruptedException e) {
      LOGGER.error("DockerCheckConnectionWorker failed", e);
      return new OutputAndStatus<>(JobStatus.FAILED, null);
    }
  }

  @Override
  public void cancel() {
    if (tapProcess != null) {
      WorkerUtils.cancelHelper(tapProcess);
    }
  }
}
