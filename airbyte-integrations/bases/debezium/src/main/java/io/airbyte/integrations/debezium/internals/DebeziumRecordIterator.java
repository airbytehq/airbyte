/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.debezium.engine.ChangeEvent;
import java.lang.reflect.Field;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.apache.kafka.connect.source.SourceRecord;
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
public class DebeziumRecordIterator<T> extends AbstractIterator<ChangeEventWithMetadata>
    implements AutoCloseableIterator<ChangeEventWithMetadata> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRecordIterator.class);

  private static final Duration SUBSEQUENT_RECORD_WAIT_TIME = Duration.ofMinutes(1);

  private final Map<Class<? extends ChangeEvent>, Field> heartbeatEventSourceField;
  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;
  private final CdcTargetPosition<T> targetPosition;
  private final Supplier<Boolean> publisherStatusSupplier;
  private final Duration firstRecordWaitTime;
  private final DebeziumShutdownProcedure<ChangeEvent<String, String>> debeziumShutdownProcedure;

  private boolean receivedFirstRecord;
  private boolean hasSnapshotFinished;
  private LocalDateTime tsLastHeartbeat;
  private T lastHeartbeatPosition;
  private int maxInstanceOfNoRecordsFound;
  private boolean signalledDebeziumEngineShutdown;

  public DebeziumRecordIterator(final LinkedBlockingQueue<ChangeEvent<String, String>> queue,
                                final CdcTargetPosition<T> targetPosition,
                                final Supplier<Boolean> publisherStatusSupplier,
                                final DebeziumShutdownProcedure<ChangeEvent<String, String>> debeziumShutdownProcedure,
                                final Duration firstRecordWaitTime) {
    this.queue = queue;
    this.targetPosition = targetPosition;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.debeziumShutdownProcedure = debeziumShutdownProcedure;
    this.firstRecordWaitTime = firstRecordWaitTime;
    this.heartbeatEventSourceField = new HashMap<>(1);

    this.receivedFirstRecord = false;
    this.hasSnapshotFinished = true;
    this.tsLastHeartbeat = null;
    this.lastHeartbeatPosition = null;
    this.maxInstanceOfNoRecordsFound = 0;
    this.signalledDebeziumEngineShutdown = false;
  }

  // The following logic incorporates heartbeat (CDC postgres only for now):
  // 1. Wait on queue either the configured time first or 1 min after a record received
  // 2. If nothing came out of queue finish sync
  // 3. If received heartbeat: check if hearbeat_lsn reached target or hasn't changed in a while
  // finish sync
  // 4. If change event lsn reached target finish sync
  // 5. Otherwise check message queuen again
  @Override
  protected ChangeEventWithMetadata computeNext() {
    // keep trying until the publisher is closed or until the queue is empty. the latter case is
    // possible when the publisher has shutdown but the consumer has not yet processed all messages it
    // emitted.
    while (!MoreBooleans.isTruthy(publisherStatusSupplier.get()) || !queue.isEmpty()) {
      final ChangeEvent<String, String> next;

      final Duration waitTime = receivedFirstRecord ? SUBSEQUENT_RECORD_WAIT_TIME : this.firstRecordWaitTime;
      try {
        next = queue.poll(waitTime.getSeconds(), TimeUnit.SECONDS);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }

      // if within the timeout, the consumer could not get a record, it is time to tell the producer to
      // shutdown.
      if (next == null) {
        if (!receivedFirstRecord || hasSnapshotFinished || maxInstanceOfNoRecordsFound >= 10) {
          requestClose(String.format("No records were returned by Debezium in the timeout seconds %s, closing the engine and iterator",
              waitTime.getSeconds()));
        }
        LOGGER.info("no record found. polling again.");
        maxInstanceOfNoRecordsFound++;
        continue;
      }

      if (isHeartbeatEvent(next)) {
        if (!hasSnapshotFinished) {
          continue;
        }

        final T heartbeatPos = getHeartbeatPosition(next);
        // wrap up sync if heartbeat position crossed the target OR heartbeat position hasn't changed for
        // too long
        if (hasSyncFinished(heartbeatPos)) {
          requestClose("Closing: Heartbeat indicates sync is done");
        }
        if (!heartbeatPos.equals(lastHeartbeatPosition)) {
          this.tsLastHeartbeat = LocalDateTime.now();
          this.lastHeartbeatPosition = heartbeatPos;
        }
        continue;
      }

      final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(next);
      hasSnapshotFinished = !changeEventWithMetadata.isSnapshotEvent();

      // if the last record matches the target file position, it is time to tell the producer to shutdown.
      if (targetPosition.reachedTargetPosition(changeEventWithMetadata)) {
        requestClose("Closing: Change event reached target position");
      }
      this.tsLastHeartbeat = null;
      this.lastHeartbeatPosition = null;
      this.receivedFirstRecord = true;
      this.maxInstanceOfNoRecordsFound = 0;
      return changeEventWithMetadata;
    }

    if (!signalledDebeziumEngineShutdown) {
      LOGGER.warn("Debezium engine has not been signalled to shutdown, this is unexpected");
    }

    // Read the records that Debezium might have fetched right at the time we called shutdown
    while (!debeziumShutdownProcedure.getRecordsRemainingAfterShutdown().isEmpty()) {
      final ChangeEvent<String, String> event;
      try {
        event = debeziumShutdownProcedure.getRecordsRemainingAfterShutdown().poll(10, TimeUnit.SECONDS);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      if (event == null || isHeartbeatEvent(event)) {
        continue;
      }
      final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(event);
      hasSnapshotFinished = !changeEventWithMetadata.isSnapshotEvent();
      return changeEventWithMetadata;
    }
    throwExceptionIfSnapshotNotFinished();
    return endOfData();
  }

  private boolean hasSyncFinished(final T heartbeatPos) {
    return targetPosition.reachedTargetPosition(heartbeatPos)
        || (heartbeatPos.equals(this.lastHeartbeatPosition) && heartbeatPosNotChanging());
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
    requestClose("Closing: Iterator closing");
  }

  private boolean isHeartbeatEvent(final ChangeEvent<String, String> event) {
    return targetPosition.isHeartbeatSupported() && Objects.nonNull(event) && !event.value().contains("source");
  }

  private boolean heartbeatPosNotChanging() {
    final Duration timeElapsedSinceLastHeartbeatTs = Duration.between(this.tsLastHeartbeat, LocalDateTime.now());
    LOGGER.debug("Time since last hb_pos change {}s", timeElapsedSinceLastHeartbeatTs.toSeconds());
    // wait time for no change in heartbeat position is half of initial waitTime
    return timeElapsedSinceLastHeartbeatTs.compareTo(this.firstRecordWaitTime.dividedBy(2)) > 0;
  }

  private void requestClose(final String closeLogMessage) {
    if (signalledDebeziumEngineShutdown) {
      return;
    }
    LOGGER.info(closeLogMessage);
    debeziumShutdownProcedure.initiateShutdownProcedure();
    signalledDebeziumEngineShutdown = true;
  }

  private void throwExceptionIfSnapshotNotFinished() {
    if (!hasSnapshotFinished) {
      throw new RuntimeException("Closing down debezium engine but snapshot has not finished");
    }
  }

  /**
   * {@link DebeziumRecordIterator#heartbeatEventSourceField} acts as a cache so that we avoid using
   * reflection to setAccessible for each event
   */
  @VisibleForTesting
  protected T getHeartbeatPosition(final ChangeEvent<String, String> heartbeatEvent) {

    try {
      final Class<? extends ChangeEvent> eventClass = heartbeatEvent.getClass();
      final Field f;
      if (heartbeatEventSourceField.containsKey(eventClass)) {
        f = heartbeatEventSourceField.get(eventClass);
      } else {
        f = eventClass.getDeclaredField("sourceRecord");
        f.setAccessible(true);
        heartbeatEventSourceField.put(eventClass, f);

        if (heartbeatEventSourceField.size() > 1) {
          LOGGER.warn("Field Cache size growing beyond expected size of 1, size is " + heartbeatEventSourceField.size());
        }
      }

      final SourceRecord sr = (SourceRecord) f.get(heartbeatEvent);
      return targetPosition.extractPositionFromHeartbeatOffset(sr.sourceOffset());
    } catch (final NoSuchFieldException | IllegalAccessException e) {
      LOGGER.info("failed to get heartbeat source offset");
      throw new RuntimeException(e);
    }
  }

}
