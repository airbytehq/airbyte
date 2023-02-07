/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.time.Duration;
import java.time.LocalDateTime;
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

  private static final Duration SUBSEQUENT_RECORD_WAIT_TIME = Duration.ofMinutes(1);

  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;
  private final CdcTargetPosition targetPosition;
  private final Supplier<Boolean> publisherStatusSupplier;
  private final VoidCallable requestClose;
  private final Duration firstRecordWaitTime;

  private boolean receivedFirstRecord;
  private boolean hasSnapshotFinished;
  private boolean signalledClose;
  private LocalDateTime tsLastHeartbeat;
  private Long lastHeartbeatPosition;
  private int maxInstanceOfNoRecordsFound;

  public DebeziumRecordIterator(final LinkedBlockingQueue<ChangeEvent<String, String>> queue,
                                final CdcTargetPosition targetPosition,
                                final Supplier<Boolean> publisherStatusSupplier,
                                final VoidCallable requestClose,
                                final Duration firstRecordWaitTime) {
    this.queue = queue;
    this.targetPosition = targetPosition;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.requestClose = requestClose;
    this.firstRecordWaitTime = firstRecordWaitTime;

    this.receivedFirstRecord = false;
    this.hasSnapshotFinished = true;
    this.signalledClose = false;
    tsLastHeartbeat = null;
    lastHeartbeatPosition = null;
    this.maxInstanceOfNoRecordsFound = 0;
  }

  // The following logic incorporates heartbeat (CDC postgres only for now):
  // 1. Wait on queue either the configured time first or 1 min after a record received
  // 2. If nothing came out of queue finish sync
  // 3. If received heartbeat: check if hearbeat_lsn reached target or hasn't changed in a while
  // finish sync
  // 4. If change event lsn reached target finish sync
  // 5. Otherwise check message queuen again
  @Override
  protected ChangeEvent<String, String> computeNext() {
    // keep trying until the publisher is closed or until the queue is empty. the latter case is
    // possible when the publisher has shutdown but the consumer has not yet processed all messages it
    // emitted.
    while (!MoreBooleans.isTruthy(publisherStatusSupplier.get()) || !queue.isEmpty()) {
      final ChangeEvent<String, String> next;

      // #18987: waitTime is still required with heartbeats for backward
      // compatibility with connectors not implementing heartbeat
      // yet (MySql, MSSql), And also due to postgres taking a long time
      // initially staying on "searching for WAL resume position"
      final Duration waitTime = receivedFirstRecord ? SUBSEQUENT_RECORD_WAIT_TIME : this.firstRecordWaitTime;
      try {
        next = queue.poll(waitTime.getSeconds(), TimeUnit.SECONDS);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }

      // if within the timeout, the consumer could not get a record, it is time to tell the producer to
      // shutdown.
      // #18987: Noticed in testing that it's possible for DBZ to be stuck "Searching for WAL resume
      // position"
      // when no changes exist. In that case queue will pop after timeout with null value for next
      if (next == null) {
        if ((!receivedFirstRecord || hasSnapshotFinished || maxInstanceOfNoRecordsFound >= 10) && !signalledClose) {
          LOGGER.info("No records were returned by Debezium in the timeout seconds {}, closing the engine and iterator", waitTime.getSeconds());
          requestClose();
        }
        LOGGER.info("no record found. polling again.");
        maxInstanceOfNoRecordsFound++;
        continue;
      }

      if (targetPosition.isHeartbeatSupported()) {
        // check if heartbeat and read hearbeat position
        LOGGER.debug("checking heartbeat lsn for: {}", next);
        final Long heartbeatPos = targetPosition.getHeartbeatPosition(next);
        if (heartbeatPos != null) {
          // wrap up sync if heartbeat position crossed the target OR heartbeat position hasn't changed for
          // too long
          if (targetPosition.reachedTargetPosition(heartbeatPos)
              || (heartbeatPos.equals(this.lastHeartbeatPosition) && heartbeatPosNotChanging()) && !signalledClose) {
            LOGGER.info("Closing: Heartbeat indicates sync is done");
            requestClose();
          }
          if (!heartbeatPos.equals(this.lastHeartbeatPosition)) {
            this.tsLastHeartbeat = LocalDateTime.now();
            this.lastHeartbeatPosition = heartbeatPos;
          }
          continue;
        }
      }

      final JsonNode eventAsJson = Jsons.deserialize(next.value());
      hasSnapshotFinished = hasSnapshotFinished(eventAsJson);

      // if the last record matches the target file position, it is time to tell the producer to shutdown.

      if (!signalledClose && shouldSignalClose(eventAsJson)) {
        LOGGER.info("Closing: Change event reached target position");
        requestClose();
      }
      this.tsLastHeartbeat = null;
      this.lastHeartbeatPosition = null;
      this.receivedFirstRecord = true;
      this.maxInstanceOfNoRecordsFound = 0;
      return next;
    }
    return endOfData();
  }

  private boolean heartbeatPosNotChanging() {
    final Duration tbt = Duration.between(this.tsLastHeartbeat, LocalDateTime.now());
    LOGGER.debug("Time since last hb_pos change {}s", tbt.toSeconds());
    // wait time for no change in heartbeat position is half of initial waitTime
    return tbt.compareTo(this.firstRecordWaitTime.dividedBy(2)) > 0;
  }

  private boolean hasSnapshotFinished(final JsonNode eventAsJson) {
    final SnapshotMetadata snapshot = SnapshotMetadata.valueOf(eventAsJson.get("source").get("snapshot").asText().toUpperCase());
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
    LOGGER.info("Closing: Iterator closing");
    requestClose();
  }

  private boolean shouldSignalClose(final JsonNode eventAsJson) {
    return targetPosition.reachedTargetPosition(eventAsJson);
  }

  private void requestClose() {
    try {
      requestClose.call();
      signalledClose = true;
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
    throwExceptionIfSnapshotNotFinished();
  }

  private void throwExceptionIfSnapshotNotFinished() {
    if (!hasSnapshotFinished) {
      throw new RuntimeException("Closing down debezium engine but snapshot has not finished");
    }
  }

}
