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

import com.google.common.collect.Streams;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardTapConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.TapFactory;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.protocol.SingerJsonIterator;
import io.dataline.workers.utils.DockerUtils;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerTapFactory implements TapFactory<SingerMessage> {
  private static final Logger LOGGER = LoggerFactory.getLogger(DockerTapFactory.class);

  private static final String INPUT_FILENAME = "input.json";

  private final String dockerImageName;

  private Process tapProcess = null;
  private InputStream stdout = null;

  public DockerTapFactory(String dockerImageName) {
    this.dockerImageName = dockerImageName;
  }

  @SuppressWarnings("UnstableApiUsage")
  @Override
  public Stream<SingerMessage> create(StandardTapConfig input, Path workspaceRoot) {

    final Path inputPath =
        WorkerUtils.writeObjectToJsonFileWorkspace(workspaceRoot, INPUT_FILENAME, input);

    try {
      String[] tapCmd =
          DockerUtils.getDockerCommand(
              workspaceRoot, dockerImageName, "--input", inputPath.toString());

      LOGGER.info("running command: {}", Arrays.toString(tapCmd));

      tapProcess =
          new ProcessBuilder()
              .command(tapCmd)
              .redirectError(workspaceRoot.resolve(DefaultSyncWorker.TAP_ERR_LOG).toFile())
              .start();

    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    stdout = tapProcess.getInputStream();
    return Streams.stream(new SingerJsonIterator(stdout)).onClose(getCloseFunction());
  }

  public Runnable getCloseFunction() {
    return () -> {
      if (stdout != null) {
        try {
          stdout.close();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      }

      WorkerUtils.cancelHelper(tapProcess);
    };
  }
}
