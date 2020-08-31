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

import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import io.dataline.workers.protocol.singer.SingerMessageTracker;
import java.nio.file.Path;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSyncWorker implements SyncWorker {
  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSyncWorker.class);

  public static final String TAP_ERR_LOG = "tap_err.log";
  public static final String TARGET_ERR_LOG = "target_err.log";

  private final TapFactory<SingerMessage> singerTapFactory;
  private final TargetFactory<SingerMessage> singerTargetFactory;

  private final AtomicBoolean cancelled;

  public DefaultSyncWorker(
      TapFactory<SingerMessage> singerTapFactory,
      TargetFactory<SingerMessage> singerTargetFactory) {
    this.singerTapFactory = singerTapFactory;
    this.singerTargetFactory = singerTargetFactory;
    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path jobRoot) {
    long startTime = System.currentTimeMillis();

    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

    final SingerMessageTracker singerMessageTracker =
        new SingerMessageTracker(syncInput.getStandardSync().getConnectionId());

    try (Stream<SingerMessage> tap = singerTapFactory.create(tapConfig, jobRoot);
        CloseableConsumer<SingerMessage> consumer =
            singerTargetFactory.create(targetConfig, jobRoot)) {

      tap.takeWhile(record -> !cancelled.get()).peek(singerMessageTracker).forEach(consumer);

    } catch (Exception e) {
      LOGGER.debug(
          "Sync worker failed. Tap error log: {}.\n Target error log: {}",
          WorkerUtils.readFileFromWorkspace(jobRoot, TAP_ERR_LOG),
          WorkerUtils.readFileFromWorkspace(jobRoot, TARGET_ERR_LOG));

      return new OutputAndStatus<>(JobStatus.FAILED, null);
    }

    StandardSyncSummary summary = new StandardSyncSummary();
    summary.setRecordsSynced(singerMessageTracker.getRecordCount());
    summary.setStartTime(startTime);
    summary.setEndTime(System.currentTimeMillis());

    final StandardSyncOutput output = new StandardSyncOutput();
    output.setStandardSyncSummary(summary);
    singerMessageTracker.getOutputState().ifPresent(output::setState);

    return new OutputAndStatus<>(cancelled.get() ? JobStatus.FAILED : JobStatus.SUCCESSFUL, output);
  }

  @Override
  public void cancel() {
    cancelled.set(true);
  }
}
