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

import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDockerDiscoveryWorker implements Worker<DiscoveryOutput> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerDockerDiscoveryWorker.class);

  private static final String CONFIG_JSON_FILENAME = "config.json";
  private static final String CATALOG_JSON_FILENAME = "catalog.json";
  private static final String ERROR_LOG_FILENAME = "err.log";

  private final String workerId;
  private final String image;
  private final Path workspacePath;
  private final String configDotJson;

  protected SingerDockerDiscoveryWorker(
      String workerId, String image, String workspaceRoot, String configDotJson) {
    this.workerId = workerId;
    this.image = image;
    this.workspacePath = Path.of(workspaceRoot, workerId);
    this.configDotJson = configDotJson;
  }

  @Override
  public OutputAndStatus<DiscoveryOutput> run() {
    prepareWorkspace();
    return runInternal();
  }

  private void prepareWorkspace() {
    try {
      FileUtils.forceMkdir(workspacePath.toFile());
      FileUtils.writeStringToFile(
          new File(workspacePath.toFile(), CONFIG_JSON_FILENAME), configDotJson, "UTF-8");
    } catch (IOException e) {
      LOGGER.error("Unable to create workspace for worker {} due to exception {} ", workerId, e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void cancel() {}

  protected OutputAndStatus<DiscoveryOutput> runInternal() {

    return null;
  }

  public static void main(String[] args) {
    File tempDirectory = FileUtils.getTempDirectory();
    System.out.println(tempDirectory);
    new SingerDockerDiscoveryWorker(
            "abc", "dataline-postgres:latest", tempDirectory.toString(), "{}")
        .run();
  }
}
