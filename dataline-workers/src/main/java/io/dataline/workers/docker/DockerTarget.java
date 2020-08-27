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
import com.google.common.base.Charsets;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardTargetConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.Target;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.utils.DockerUtils;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerTarget implements Target<SingerMessage> {
  private static final Logger LOGGER = LoggerFactory.getLogger(DockerTarget.class);

  private static final String CONFIG_JSON_FILENAME = "input.json";

  private final String dockerImageName;
  private Process targetProcess;

  public DockerTarget(String dockerImageName) {
    this.dockerImageName = dockerImageName;
  }

  @Override
  public void consume(
      Stream<SingerMessage> data, StandardTargetConfig targetConfig, Path workspacePath) {

    final Path configPath =
        WorkerUtils.writeObjectToJsonFileWorkspace(
            workspacePath, CONFIG_JSON_FILENAME, targetConfig);

    String[] dockerCmd =
        DockerUtils.getDockerCommand(
            workspacePath, dockerImageName, "--config", configPath.toString());

    try {
      targetProcess =
          new ProcessBuilder()
              .command(dockerCmd)
              .redirectError(workspacePath.resolve(DefaultSyncWorker.TARGET_ERR_LOG).toFile())
              .start();

      try (BufferedWriter writer =
          new BufferedWriter(
              new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8))) {

        final ObjectMapper objectMapper = new ObjectMapper();
        data.forEach(
            record -> {
              try {
                writer.write(objectMapper.writeValueAsString(record));
                writer.newLine();
              } catch (IOException e) {
                throw new RuntimeException(e);
              }
            });
      }

    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    try {
      while (!targetProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug(
            "Waiting for sync worker (job:{}) target", ""); // TODO when job id is passed in
      }
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() {
    WorkerUtils.cancelHelper(targetProcess);
  }
}
