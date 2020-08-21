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

import io.dataline.config.JobSyncConfig;
import io.dataline.config.JobSyncOutput;
import io.dataline.config.JobSyncTapConfig;
import io.dataline.config.JobSyncTargetConfig;

// T in this case is our protocol for communicating between tap and target. Likely we'll need to
// open this up and have the protocol of the tap and that of the target and then dynamically we swap
// in any protocol converter that we might need. Keeping it simple for now and assuming one
// protocol--just using the singer protocol for point of example right now. #ijusttriggeredmichel.
public class DefaultSyncWorker<T> implements SyncWorker {
  private final SyncTap<T> tap;
  private final SyncTarget<T> target;

  public DefaultSyncWorker(SyncTap<T> tap, SyncTarget<T> target) {
    this.tap = tap;
    this.target = target;
  }

  @Override
  public OutputAndStatus<JobSyncOutput> run(JobSyncConfig syncConfig, String workspacePath) {

    final JobSyncTapConfig tapConfig = new JobSyncTapConfig();
    tapConfig.setSourceConnectionImplementation(syncConfig.getSourceConnectionImplementation());
    tapConfig.setStandardSync(syncConfig.getStandardSync());

    final JobSyncTargetConfig targetConfig = new JobSyncTargetConfig();
    targetConfig.setDestinationConnectionImplementation(
        syncConfig.getDestinationConnectionImplementation());
    targetConfig.setStandardSync(syncConfig.getStandardSync());

    final JobSyncOutput output =
        target.run(tap.run(tapConfig, workspacePath), targetConfig, workspacePath);

    // todo (cgardens) - OutputAndStatus doesn't really work here. it's like both tap and target
    //   need to return a promise for OutputAndStatus creation. But then that's kinda confusing too.
    return new OutputAndStatus<>(JobStatus.SUCCESSFUL, output);
  }

  @Override
  public void cancel() {}
}
