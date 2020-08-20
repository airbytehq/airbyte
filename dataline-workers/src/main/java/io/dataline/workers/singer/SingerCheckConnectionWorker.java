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

import io.dataline.config.StandardConnectionStatus;
import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerCheckConnectionWorker extends BaseSingerWorker<StandardConnectionStatus> {
  private final Logger LOGGER = LoggerFactory.getLogger(SingerCheckConnectionWorker.class);
  private SingerDiscoveryWorker singerDiscoveryWorker;

  public SingerCheckConnectionWorker(
      String workerId,
      SingerTap singerTap,
      String configDotJson,
      String workspaceRoot,
      String singerLibsRoot) {
    super(workerId, workspaceRoot, singerLibsRoot);
    this.singerDiscoveryWorker =
        new SingerDiscoveryWorker(
            workerId, configDotJson, singerTap, workspaceRoot, singerLibsRoot);
  }

  @Override
  OutputAndStatus<StandardConnectionStatus> runInternal() {
    OutputAndStatus<DiscoveryOutput> outputAndStatus = singerDiscoveryWorker.runInternal();
    StandardConnectionStatus connectionStatus = new StandardConnectionStatus();
    JobStatus jobStatus;
    if (outputAndStatus.getStatus() == JobStatus.SUCCESSFUL
        && outputAndStatus.getOutput().isPresent()) {
      connectionStatus.setStatus(StandardConnectionStatus.Status.SUCCESS);
      jobStatus = JobStatus.SUCCESSFUL;
    } else {
      LOGGER.info(
          "Connection check for worker {} unsuccessful. Discovery output: {}",
          workerId,
          outputAndStatus);
      jobStatus = JobStatus.FAILED;
      connectionStatus.setStatus(StandardConnectionStatus.Status.FAILURE);
      // TODO add better error log parsing to specify the exact reason for failure as the message
      // fieldk
    }
    return new OutputAndStatus<>(jobStatus, connectionStatus);
  }

  @Override
  public void cancel() {
    singerDiscoveryWorker.cancel();
  }
}
