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

import io.dataline.config.JobSyncOutput;
import io.dataline.workers.OutputAndStatus;

public class SingerSyncWorker extends BaseSingerWorker<JobSyncOutput> {
  private static final String TAP_CONFIG_FILENAME = "tap_config.json";
  private static final String CATALOG_FILENAME = "catalog.json";
  private static final String STATE_FILENAME = "state.json";
  private static final String TARGET_CONFIG_FILENAME = "target_config.json";

  private static final String TAP_ERR_LOG = "tap_err.log";
  private static final String TARGET_ERR_LOG = "target_err.log";
  private static final String OUTPUT_STATE_FILENAME =

  private final SingerTap tap;
  private final String tapConfiguration;
  private final String tapCatalog;
  private final String connectionState;
  private final SingerTarget target;
  private final String targetConfig;

  private Process workerProcess;

  public SingerSyncWorker(
      String workerId,
      String workspaceRoot,
      String singerRoot,
      SingerTap tap,
      String tapConfiguration,
      String tapCatalog,
      String connectionState,
      SingerTarget target,
      String targetConfig) {
    super(workerId, workspaceRoot, singerRoot);
    this.tap = tap;
    this.tapConfiguration = tapConfiguration;
    this.tapCatalog = tapCatalog;
    this.connectionState = connectionState;
    this.target = target;
    this.targetConfig = targetConfig;
  }

  @Override
  OutputAndStatus<JobSyncOutput> runInternal() {
    String tapConfigPath = writeFileToWorkspace(TAP_CONFIG_FILENAME, tapConfiguration);
    String catalogPath = writeFileToWorkspace(CATALOG_FILENAME, tapCatalog);
    String connectionPath = writeFileToWorkspace(STATE_FILENAME, connectionState);
    String targetConfigPath = writeFileToWorkspace(TARGET_CONFIG_FILENAME, targetConfig);

    // tap | record counter | target
    ProcessBuilder pb = new ProcessBuilder().command(getExecutableAbsolutePath(tap), "--config", tapConfigPath, "--catalog", catalogPath, "--state", connectionState).redirec;

  }

  @Override
  public void cancel() {
    cancelHelper(workerProcess);
  }
}
