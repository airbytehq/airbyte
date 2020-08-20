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

package io.dataline.workers.singer;

import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseSingerWorker<InputType, OutputType>
    implements Worker<InputType, OutputType> {
  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSingerWorker.class);

  protected JobStatus jobStatus;

  private final String singerExecutablePath;

  protected BaseSingerWorker(String singerExecutablePath) {
    this.singerExecutablePath = singerExecutablePath;
  }

  @Override
  public OutputAndStatus<OutputType> run(InputType inputType, String workspaceRoot) {
    return runInternal(inputType, workspaceRoot);
  }

  abstract OutputAndStatus<OutputType> runInternal(InputType inputType, String workspaceRoot);

  protected void cancelHelper(Process workerProcess) {
    try {
      jobStatus = JobStatus.FAILED;
      workerProcess.destroy();
      workerProcess.waitFor(10, TimeUnit.SECONDS);
      if (workerProcess.isAlive()) {
        workerProcess.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when cancelling job.", e);
    }
  }

  protected String readFileFromWorkspace(String workspaceRoot, String fileName) {
    try (FileReader fileReader = new FileReader(getWorkspaceFilePath(workspaceRoot, fileName));
        BufferedReader br = new BufferedReader(fileReader)) {
      return br.lines().collect(Collectors.joining("\n"));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String writeFileToWorkspace(String workspaceRoot, String fileName, String contents) {
    String filePath = getWorkspaceFilePath(workspaceRoot, fileName);
    try (FileWriter fileWriter = new FileWriter(filePath)) {
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String getExecutableAbsolutePath() {
    return singerExecutablePath;
  }

  private String getWorkspaceFilePath(String workspaceRoot, String fileName) {
    return Path.of(workspaceRoot).resolve(fileName).toAbsolutePath().toString();
  }
}
