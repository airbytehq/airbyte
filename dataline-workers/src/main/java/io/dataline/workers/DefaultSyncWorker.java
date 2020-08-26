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

import io.dataline.config.SingerProtocol;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import io.dataline.config.State;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.commons.lang3.mutable.MutableLong;

// T in this case is our protocol for communicating between tap and target. Likely we'll need to
// open this up and have the protocol of the tap and that of the target and then dynamically we swap
// in any protocol converter that we might need. Keeping it simple for now and assuming one
// protocol--just using the singer protocol for point of example right now. #ijusttriggeredmichel.
public class DefaultSyncWorker implements SyncWorker {
  private final SyncTap<SingerProtocol> tap;
  private final SyncTarget<SingerProtocol> target;

  public DefaultSyncWorker(SyncTap<SingerProtocol> tap, SyncTarget<SingerProtocol> target) {
    this.tap = tap;
    this.target = target;
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path workspacePath)
      throws InvalidCredentialsException, InvalidCatalogException {
    long startTime = System.currentTimeMillis();

    final StandardTapConfig tapConfig = new StandardTapConfig();
    tapConfig.setSourceConnectionImplementation(syncInput.getSourceConnectionImplementation());
    tapConfig.setStandardSync(syncInput.getStandardSync());

    final StandardTargetConfig targetConfig = new StandardTargetConfig();
    targetConfig.setDestinationConnectionImplementation(
        syncInput.getDestinationConnectionImplementation());
    targetConfig.setStandardSync(syncInput.getStandardSync());

    final Iterator<SingerProtocol> iterator = tap.run(tapConfig, workspacePath);

    final MutableLong recordCount = new MutableLong();
    Consumer<SingerProtocol> counter =
        record -> {
          if (record.getType().equals(SingerProtocol.Type.RECORD)) {
            recordCount.increment();
          }
        };
    Iterator<SingerProtocol> countingIterator = new ConsumerIterator<>(iterator, counter);

    final State state = target.run(countingIterator, targetConfig, workspacePath);

    StandardSyncSummary summary = new StandardSyncSummary();
    summary.setRecordsSynced(recordCount.getValue());
    summary.setStartTime(startTime);
    summary.setEndTime(System.currentTimeMillis());
    summary.setJobId(UUID.randomUUID()); // TODO this is not input anywhere
    // TODO set logs

    final StandardSyncOutput output = new StandardSyncOutput();
    output.setStandardSyncSummary(summary);
    output.setState(state);

    return new OutputAndStatus<>(JobStatus.SUCCESSFUL, output);
  }

  @Override
  public void cancel() {}
}
