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

package io.dataline.workers.protocols.singer;

import io.dataline.commons.io.IOs;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import io.dataline.config.State;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.SyncWorker;
import io.dataline.workers.WorkerUtils;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerSyncWorker implements SyncWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerSyncWorker.class);

  public static final String TAP_ERR_LOG = "tap_err.log";
  public static final String TARGET_ERR_LOG = "target_err.log";

  private final SingerTap singerTap;
  private final SingerTarget singerTarget;

  private final AtomicBoolean cancelled;

  public SingerSyncWorker(SingerTap singerTap,
                          SingerTarget singerTarget) {
    this.singerTap = singerTap;
    this.singerTarget = singerTarget;
    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path jobRoot) {
    long startTime = System.currentTimeMillis();

    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

    final SingerMessageTracker singerMessageTracker = new SingerMessageTracker();

    try (singerTarget; singerTap) {

      singerTarget.start(targetConfig, jobRoot);
      singerTap.start(tapConfig, jobRoot);

      while (!cancelled.get() && !singerTap.isFinished()) {
        final Optional<SingerMessage> maybeMessage = singerTap.attemptRead();
        if (maybeMessage.isPresent()) {
          final SingerMessage message = maybeMessage.get();
          singerMessageTracker.accept(message);
          singerTarget.accept(message);
        }
      }

      singerTarget.notifyEndOfStream();

    } catch (Exception e) {
      LOGGER.error("Sync worker failed. Tap error log: {}.\n Target error log: {}",
          Files.exists(jobRoot.resolve(TAP_ERR_LOG)) ? IOs.readFile(jobRoot, TAP_ERR_LOG) : "<null>",
          Files.exists(jobRoot.resolve(TARGET_ERR_LOG)) ? IOs.readFile(jobRoot, TARGET_ERR_LOG) : "<null>",
          e);

      return new OutputAndStatus<>(JobStatus.FAILED, null);
    }

    StandardSyncSummary summary = new StandardSyncSummary()
        .withRecordsSynced(singerMessageTracker.getRecordCount())
        .withStartTime(startTime)
        .withEndTime(System.currentTimeMillis());

    final StandardSyncOutput output = new StandardSyncOutput().withStandardSyncSummary(summary);
    singerMessageTracker.getOutputState().ifPresent(singerState -> {
      final State state = new State()
          .withConnectionId(tapConfig.getStandardSync().getConnectionId())
          .withState(singerState);
      output.withState(state);
    });

    return new OutputAndStatus<>(cancelled.get() ? JobStatus.FAILED : JobStatus.SUCCESSFUL, output);
  }

  @Override
  public void cancel() {
    cancelled.set(true);
  }

}
