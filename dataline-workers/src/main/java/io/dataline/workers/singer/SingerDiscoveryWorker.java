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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;

public class SingerDiscoveryWorker extends BaseSingerWorker<DiscoveryOutput> {
  // TODO log errors to specified file locations
  private static Logger LOGGER = LoggerFactory.getLogger(SingerDiscoveryWorker.class);
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private final String configDotJson;
  private final SingerTap tap;
  private volatile Process workerProcess;

  public SingerDiscoveryWorker(
      String workerId,
      String configDotJson,
      SingerTap tap,
      String workspaceRoot,
      String singerLibsRoot) {
    super(workerId, workspaceRoot, singerLibsRoot);
    this.configDotJson = configDotJson;
    this.tap = tap;
  }

  @Override
  OutputAndStatus<DiscoveryOutput> runInternal() {
    // TODO use format converter here
    // write config.json to disk
    String configPath = writeFileToWorkspace(CONFIG_JSON_FILENAME, configDotJson);

    String tapPath = getExecutableAbsolutePath(tap);

    String catalogDotJsonPath =
        getWorkspacePath().resolve(CATALOG_JSON_FILENAME).toAbsolutePath().toString();
    String errorLogPath =
        getWorkspacePath().resolve(ERROR_LOG_FILENAME).toAbsolutePath().toString();

    // exec
    try {
      String[] cmd = {tapPath, "--config", configPath, "--discover"};

      workerProcess =
          new ProcessBuilder(cmd)
              .redirectError(new File(errorLogPath))
              .redirectOutput(new File(catalogDotJsonPath))
              .start();

      while (!workerProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.info("Waiting for discovery worker {}", workerId);
      }

      int exitCode = workerProcess.exitValue();
      if (exitCode == 0) {
        String catalog = readFileFromWorkspace(CATALOG_JSON_FILENAME);
        return new OutputAndStatus<>(SUCCESSFUL, new DiscoveryOutput(catalog));
      } else {
        String errLog = readFileFromWorkspace(ERROR_LOG_FILENAME);
        LOGGER.debug(
            "Discovery worker {} subprocess finished with exit code {}. Error log: {}",
            workerId,
            exitCode,
            errLog);
        return new OutputAndStatus<>(FAILED);
      }
    } catch (IOException | InterruptedException e) {
      LOGGER.error("Exception running discovery: ", e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void cancel() {
    cancelHelper(workerProcess);
  }
}
