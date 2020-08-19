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
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseSingerWorker<OutputType> implements Worker<OutputType> {
  private static Logger LOGGER = LoggerFactory.getLogger(BaseSingerWorker.class);

  protected JobStatus jobStatus;
  protected String workerId;
  protected final Path workspacePath;

  private final String singerRoot;

  protected BaseSingerWorker(String workerId, String workspaceRoot, String singerRoot) {
    this.workerId = workerId;
    this.workspacePath = Path.of(workspaceRoot, workerId);
    this.singerRoot = singerRoot;
  }

  @Override
  public OutputAndStatus<OutputType> run() {
    createWorkspace();
    return runInternal();
  }

  public abstract OutputAndStatus<OutputType> runInternal();

  private void createWorkspace() {
    try {
      FileUtils.forceMkdir(workspacePath.toFile());
    } catch (IOException e) {
      LOGGER.error("Unable to create workspace for worker {} due to exception {} ", workerId, e);
      throw new RuntimeException(e);
    }
  }

  protected void cancelHelper(Process workerProcess) {
    try {
      jobStatus = JobStatus.FAILED;
      workerProcess.destroy();
      workerProcess.waitFor(10, TimeUnit.SECONDS);
      if (workerProcess.isAlive()) {
        workerProcess.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when cancelling worker " + workerId, e);
    }
  }

  protected Path getWorkspacePath() {
    return workspacePath;
  }

  protected String readFileFromWorkspace(String fileName) {
    try (FileReader fileReader = new FileReader(getWorkspaceFilePath(fileName));
        BufferedReader br = new BufferedReader(fileReader)) {
      return br.lines().collect(Collectors.joining("\n"));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String writeFileToWorkspace(String fileName, String contents) {
    String filePath = getWorkspaceFilePath(fileName);
    try (FileWriter fileWriter = new FileWriter(filePath)) {
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected String getExecutableAbsolutePath(SingerConnector tapOrTarget) {
    return Paths.get(
            singerRoot,
            tapOrTarget.getPythonVirtualEnvName(),
            "bin",
            tapOrTarget.getExecutableName())
        .toAbsolutePath()
        .toString();
  }

  private String getWorkspaceFilePath(String fileName) {
    return getWorkspacePath().resolve(fileName).toAbsolutePath().toString();
  }
}
