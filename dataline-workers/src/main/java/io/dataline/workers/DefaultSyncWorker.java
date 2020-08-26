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

import io.dataline.config.JobSyncOutput;
import io.dataline.config.JobSyncTapConfig;
import io.dataline.config.JobSyncTargetConfig;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.State;

import java.nio.file.Path;
import java.util.Iterator;
import java.util.UUID;

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
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path workspacePath) {
    long startTime = System.currentTimeMillis();

    final JobSyncTapConfig tapConfig = new JobSyncTapConfig();
    tapConfig.setSourceConnectionImplementation(syncInput.getSourceConnectionImplementation());
    tapConfig.setStandardSync(syncInput.getStandardSync());

    final JobSyncTargetConfig targetConfig = new JobSyncTargetConfig();
    targetConfig.setDestinationConnectionImplementation(
        syncInput.getDestinationConnectionImplementation());
    targetConfig.setStandardSync(syncInput.getStandardSync());

    final Iterator<T> iterator = tap.run(tapConfig, workspacePath);
    final ItrSpy itrSpy = new ItrSpy();
    Iterator<T> countingIterator = new BlahIterator(iterator, itrSpy);

    final State state = target.run(countingIterator, targetConfig, workspacePath);

    StandardSyncSummary summary = new StandardSyncSummary();
    summary.setRecordsSynced(itrSpy.getCount());
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

  public class BlahIterator implements Iterator<T> {

    private final Iterator<T> iterator;
    private final ItrSpy spy;

    public BlahIterator(Iterator<T> iterator, ItrSpy spy) {
      this.iterator = iterator;
      this.spy = spy;
    }

    @Override
    public boolean hasNext() {
      return iterator.hasNext();
    }

    @Override
    public T next() {
      final T next = iterator.next();
      spy.incrementNumRecords();

      return next;
    }
  }

  public static class ItrSpy {
    private long count;

    public ItrSpy() {
      count = 0;
    }

    public void incrementNumRecords() {
      count++;
    }

    public long getCount() {
      return count;
    }
  }
}
