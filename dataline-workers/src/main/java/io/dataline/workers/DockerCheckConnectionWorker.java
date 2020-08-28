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

package io.dataline.workers;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
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
      StandardCheckConnectionInput standardCheckConnectionInput, Path jobRoot) {
    final ObjectMapper objectMapper = new ObjectMapper();

    // write input struct to docker image
    final String inputString;
    try {
      inputString = objectMapper.writeValueAsString(standardCheckConnectionInput);
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    final Path configPath =
        WorkerUtils.writeFileToWorkspace(jobRoot, INPUT, inputString); // wrong type

    // run it. patiently.
    try {
      String[] tapCmd = {
        "docker", "run", jobRoot.toString(), imageName, "--config", configPath.toString()
      };

      LOGGER.debug("Tap command: {}", String.join(" ", tapCmd));

      tapProcess = new ProcessBuilder().command(tapCmd).start();

      while (!tapProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug("Waiting for worker");
      }

      // read output struct. assume it is written to correct place.
      final String outputString = WorkerUtils.readFileFromWorkspace(jobRoot, OUTPUT);
      final StandardCheckConnectionOutput standardCheckConnectionOutput =
          objectMapper.readValue(outputString, StandardCheckConnectionOutput.class);

      return new OutputAndStatus<>(JobStatus.SUCCESSFUL, standardCheckConnectionOutput);
    } catch (IOException | InterruptedException e) {
      LOGGER.error("DockerCheckConnectionWorker failed", e);
      return new OutputAndStatus<>(JobStatus.FAILED, null);
    }
  }

  @Override
  public void cancel() {
    if (tapProcess != null) {
      WorkerUtils.cancelProcess(tapProcess);
    }
  }
}
