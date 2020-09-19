/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.workers.protocols.singer;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.singer.SingerMessage;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.SyncWorker;
import io.airbyte.workers.WorkerUtils;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerSyncWorker implements SyncWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerSyncWorker.class);

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
      LOGGER.error("Sync worker failed.", e);

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
