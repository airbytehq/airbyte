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

package io.airbyte.integrations.source.postgres;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.PgLsn;
import io.debezium.engine.ChangeEvent;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.source.SourceRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The record consumer is responsible for 1. making sure every record produced by the record
 * publisher is processed 2. signalling to the record publisher when it is time for it to stop
 * producing records. It emits this signal either when the publisher had not produced a new record
 * for a long time or when it has processed at least all of the records that were present in the
 * database when the source was started. Because the publisher might publish more records between
 * the consumer sending this signal and the publisher acutally shutting down, the consumer must stay
 * alive as long as the publisher is not closed or if there are any new records for it to process
 * (even if the publisher is closed).
 */
public class DebeziumRecordConsumer extends AbstractIterator<ChangeEvent<String, String>>
    implements AutoCloseableIterator<ChangeEvent<String, String>> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRecordConsumer.class);

  private static final TimeUnit SLEEP_TIME_UNIT = TimeUnit.SECONDS;
  private static final int SLEEP_TIME_AMOUNT = 5;

  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;
  private final PgLsn targetLsn;
  private final Supplier<Boolean> publisherStatusSupplier;
  private final VoidCallable requestClose;
  private final Instant emittedAt;

  public DebeziumRecordConsumer(LinkedBlockingQueue<ChangeEvent<String, String>> queue,
                                PgLsn targetLsn,
                                Supplier<Boolean> publisherStatusSupplier,
                                VoidCallable requestClose,
                                Instant emittedAt) {
    this.queue = queue;
    this.targetLsn = targetLsn;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.requestClose = requestClose;
    this.emittedAt = emittedAt;
  }

  @Override
  protected ChangeEvent<String, String> computeNext() {
    // keep trying until the publisher is closed or until the queue is empty. the latter case is
    // possible when the publisher has shutdown but the consumer has not yet processed all messages it
    // emitted.
    while (!MoreBooleans.isTruthy(publisherStatusSupplier.get()) || !queue.isEmpty()) {
      final ChangeEvent<String, String> next;
      try {
        next = queue.poll(SLEEP_TIME_AMOUNT, SLEEP_TIME_UNIT);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }

      // if within the timeout, the consumer could not get a record, it is time to tell the producer to
      // shutdown.
      if (next == null) {
        requestClose();
        LOGGER.info("no record found. polling again.");
        continue;
      }

      // if the last record matches the target lsn, it is time to tell the producer to shutdown.
      if (shouldSignalClose(next)) {
        requestClose();
      }

      return next;
    }
    return endOfData();
  }

  @Override
  public void close() throws Exception {
    requestClose.call();
  }

  private boolean shouldSignalClose(ChangeEvent<String, String> event) {
    final PgLsn eventLsn = extractLsn(event);

    if (targetLsn.compareTo(eventLsn) > 0) {
      return false;
    } else {
      final SnapshotMetadata snapshotMetadata = getSnapshotMetadata(event);
      // if not snapshot or is snapshot but last record in snapshot.
      return SnapshotMetadata.TRUE != snapshotMetadata;
    }
  }

  private SnapshotMetadata getSnapshotMetadata(ChangeEvent<String, String> event) {
    try {
      final Method sourceRecordMethod = event.getClass().getMethod("sourceRecord");
      sourceRecordMethod.setAccessible(true);
      final SourceRecord sourceRecord = (SourceRecord) sourceRecordMethod.invoke(event);
      final String snapshot = ((Struct) sourceRecord.value()).getStruct("source").getString("snapshot");

      if (snapshot == null) {
        return null;
      }

      // the snapshot field is an enum of true, false, and last.
      return SnapshotMetadata.valueOf(snapshot.toUpperCase());
    } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
      throw new RuntimeException(e);
    }
  }

  private PgLsn extractLsn(ChangeEvent<String, String> event) {
    return Optional.ofNullable(event.value())
        .flatMap(value -> Optional.ofNullable(Jsons.deserialize(value).get("source")))
        .flatMap(source -> Optional.ofNullable(source.get("lsn").asText()))
        .map(Long::parseLong)
        .map(PgLsn::fromLong)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

  private void requestClose() {
    try {
      requestClose.call();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  enum SnapshotMetadata {
    TRUE,
    FALSE,
    LAST
  }

}
