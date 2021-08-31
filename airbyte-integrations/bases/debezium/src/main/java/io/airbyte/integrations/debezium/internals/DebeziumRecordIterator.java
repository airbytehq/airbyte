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

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.debezium.engine.ChangeEvent;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The record iterator is the consumer (in the producer / consumer relationship with debezium)
 * responsible for 1. making sure every record produced by the record publisher is processed 2.
 * signalling to the record publisher when it is time for it to stop producing records. It emits
 * this signal either when the publisher had not produced a new record for a long time or when it
 * has processed at least all of the records that were present in the database when the source was
 * started. Because the publisher might publish more records between the consumer sending this
 * signal and the publisher actually shutting down, the consumer must stay alive as long as the
 * publisher is not closed. Even after the publisher is closed, the consumer will finish processing
 * any produced records before closing.
 */
public class DebeziumRecordIterator extends AbstractIterator<ChangeEvent<String, String>>
    implements AutoCloseableIterator<ChangeEvent<String, String>> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRecordIterator.class);

  private static final WaitTime FIRST_RECORD_WAIT_TIME_MINUTES = new WaitTime(5, TimeUnit.MINUTES);
  private static final WaitTime SUBSEQUENT_RECORD_WAIT_TIME_SECONDS = new WaitTime(1, TimeUnit.MINUTES);

  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;
  private final CdcTargetPosition targetPosition;
  private final Supplier<Boolean> publisherStatusSupplier;
  private final VoidCallable requestClose;
  private boolean receivedFirstRecord;
  private boolean hasSnapshotFinished;
  private boolean signalledClose;

  public DebeziumRecordIterator(LinkedBlockingQueue<ChangeEvent<String, String>> queue,
                                CdcTargetPosition targetPosition,
                                Supplier<Boolean> publisherStatusSupplier,
                                VoidCallable requestClose) {
    this.queue = queue;
    this.targetPosition = targetPosition;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.requestClose = requestClose;
    this.receivedFirstRecord = false;
    this.hasSnapshotFinished = true;
    this.signalledClose = false;
  }

  @Override
  protected ChangeEvent<String, String> computeNext() {
    // keep trying until the publisher is closed or until the queue is empty. the latter case is
    // possible when the publisher has shutdown but the consumer has not yet processed all messages it
    // emitted.
    while (!MoreBooleans.isTruthy(publisherStatusSupplier.get()) || !queue.isEmpty()) {
      final ChangeEvent<String, String> next;
      try {
        WaitTime waitTime = receivedFirstRecord ? SUBSEQUENT_RECORD_WAIT_TIME_SECONDS : FIRST_RECORD_WAIT_TIME_MINUTES;
        next = queue.poll(waitTime.period, waitTime.timeUnit);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }

      // if within the timeout, the consumer could not get a record, it is time to tell the producer to
      // shutdown.
      if (next == null) {
        LOGGER.info("Closing cause next is returned as null");
        requestClose();
        LOGGER.info("no record found. polling again.");
        continue;
      }

      JsonNode eventAsJson = Jsons.deserialize(next.value());
      hasSnapshotFinished = hasSnapshotFinished(eventAsJson);

      // if the last record matches the target file position, it is time to tell the producer to shutdown.
      if (!signalledClose && shouldSignalClose(eventAsJson)) {
        requestClose();
      }
      receivedFirstRecord = true;
      return next;
    }
    return endOfData();
  }

  private boolean hasSnapshotFinished(JsonNode eventAsJson) {
    SnapshotMetadata snapshot = SnapshotMetadata.valueOf(eventAsJson.get("source").get("snapshot").asText().toUpperCase());
    return SnapshotMetadata.TRUE != snapshot;
  }

  /**
   * Debezium was built as an ever running process which keeps on listening for new changes on DB and
   * immediately processing them. Airbyte needs debezium to work as a start stop mechanism. In order
   * to determine when to stop debezium engine we rely on few factors 1. TargetPosition logic. At the
   * beginning of the sync we define a target position in the logs of the DB. This can be an LSN or
   * anything specific to the DB which can help us identify that we have reached a specific position
   * in the log based replication When we start processing records from debezium, we extract the the
   * log position from the metadata of the record and compare it with our target that we defined at
   * the beginning of the sync. If we have reached the target position, we shutdown the debezium
   * engine 2. The TargetPosition logic might not always work and in order to tackle that we have
   * another logic where if we do not receive records from debezium for a given duration, we ask
   * debezium engine to shutdown 3. We also take the Snapshot into consideration, when a connector is
   * running for the first time, we let it complete the snapshot and only after the completion of
   * snapshot we should shutdown the engine. If we are closing the engine before completion of
   * snapshot, we throw an exception
   */
  @Override
  public void close() throws Exception {
    requestClose();
  }

  private boolean shouldSignalClose(JsonNode eventAsJson) {
    return targetPosition.reachedTargetPosition(eventAsJson);
  }

  private void requestClose() {
    try {
      requestClose.call();
      signalledClose = true;
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
    throwExceptionIfSnapshotNotFinished();
  }

  private void throwExceptionIfSnapshotNotFinished() {
    if (!hasSnapshotFinished) {
      throw new RuntimeException("Closing down debezium engine but snapshot has not finished");
    }
  }

  private static class WaitTime {

    public final int period;
    public final TimeUnit timeUnit;

    public WaitTime(int period, TimeUnit timeUnit) {
      this.period = period;
      this.timeUnit = timeUnit;
    }

  }

}
