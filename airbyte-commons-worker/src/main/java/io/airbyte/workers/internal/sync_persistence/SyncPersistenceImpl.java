/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.sync_persistence;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.converters.StateConverter;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.workers.internal.state_aggregator.StateAggregator;
import io.airbyte.workers.internal.state_aggregator.StateAggregatorFactory;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class SyncPersistenceImpl implements SyncPersistence {

  final long RUN_IMMEDIATELY = 0;
  final long FLUSH_TERMINATION_TIMEOUT_IN_SECONDS = 60;

  private final UUID connectionId;
  private final StateApi stateApi;
  private final StateAggregatorFactory stateAggregatorFactory;

  private StateAggregator stateBuffer;
  private StateAggregator stateToFlush;
  private final ScheduledExecutorService stateFlushExecutorService;
  private ScheduledFuture<?> stateFlushFuture;
  private final long stateFlushPeriodInSeconds;

  public SyncPersistenceImpl(final UUID connectionId,
                             final StateApi stateApi,
                             final StateAggregatorFactory stateAggregatorFactory,
                             final ScheduledExecutorService scheduledExecutorService,
                             long stateFlushPeriodInSeconds) {
    this.connectionId = connectionId;
    this.stateApi = stateApi;
    this.stateAggregatorFactory = stateAggregatorFactory;
    this.stateFlushExecutorService = scheduledExecutorService;
    this.stateBuffer = this.stateAggregatorFactory.create();
    this.stateFlushPeriodInSeconds = stateFlushPeriodInSeconds;
  }

  @Override
  public void persist(AirbyteStateMessage stateMessage) {
    stateBuffer.ingest(stateMessage);
    startBackgroundFlushStateTask();
  }

  private void startBackgroundFlushStateTask() {
    if (stateFlushFuture != null) {
      return;
    }

    // Making sure we only start one of background flush task
    synchronized (this) {
      if (stateFlushFuture == null) {
        stateFlushFuture =
            stateFlushExecutorService.scheduleAtFixedRate(this::flushState, RUN_IMMEDIATELY, stateFlushPeriodInSeconds, TimeUnit.SECONDS);
      }
    }
  }

  /**
   * Stop background data flush thread and attempt to flush pending data
   *
   * If there is already flush in progress, wait for it to terminate. If it didn't terminate during
   * the allocated time, we exit rather than attempting a concurrent write that could lead to
   * non-deterministic behavior.
   *
   * For the final flush, we will retry in case of failures since there is no more "scheduled" attempt
   * after this.
   */
  @Override
  public void close() {
    // stop the buffered refresh
    stateFlushExecutorService.shutdown();

    // Wait for previous running task to terminate
    try {
      final boolean terminated = stateFlushExecutorService.awaitTermination(FLUSH_TERMINATION_TIMEOUT_IN_SECONDS, TimeUnit.SECONDS);
      if (!terminated) {
        // Ongoing flush failed to terminate within the allocated time
        log.info("Pending persist operation took too long to complete, most recent states may have been lost");

        // This is the hard case, if the backend persisted the data, we may write duplicate
        // We exit to avoid non-deterministic write attempts
        return;
      }
    } catch (final InterruptedException e) {
      // The current thread is getting interrupted
      // TODO Metrics
      log.info("SyncPersistence has been interrupted while terminating, most recent states may have been lost", e);

      // This is also a hard case, if the backend persisted the data, we may write duplicate
      // We exit to avoid non-deterministic write attempts
      return;
    }

    if (hasDataToFlush()) {
      // we still have data to flush
      prepareDataForFlush();
      AirbyteApiClient.retryWithJitter(() -> {
        doFlushState();
        return null;
      }, "Flush States from SyncPersistenceImpl");
    }
  }

  private boolean hasDataToFlush() {
    return !stateBuffer.isEmpty() || stateToFlush != null;
  }

  /**
   * FlushState method for the ScheduledExecutorService
   *
   * This method is swallowing exceptions on purpose. We do not want to fail or retry in a regular
   * run, the retry is deferred to the next run which will merge the data from the previous failed
   * attempt and the recent buffered data.
   */
  private void flushState() {
    prepareDataForFlush();

    try {
      doFlushState();
    } catch (final Exception e) {
      log.warn("Failed to persist state for connectionId {}", connectionId, e);
    }
  }

  private void prepareDataForFlush() {
    final StateAggregator stateBufferToFlush = stateBuffer;
    stateBuffer = stateAggregatorFactory.create();

    if (stateToFlush == null) {
      // Happy path, previous flush was successful
      stateToFlush = stateBufferToFlush;
    } else {
      // Merging states from the previous attempt with the incoming buffer to flush
      stateToFlush.ingest(stateBufferToFlush);
    }
  }

  private void doFlushState() throws ApiException {
    if (stateToFlush.isEmpty()) {
      return;
    }

    final State state = stateToFlush.getAggregated();
    final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), true);

    if (maybeStateWrapper.isEmpty()) {
      return;
    }

    final ConnectionStateCreateOrUpdate stateApiRequest = new ConnectionStateCreateOrUpdate()
        .connectionId(connectionId)
        .connectionState(StateConverter.toClient(connectionId, maybeStateWrapper.get()));

    stateApi.createOrUpdateState(stateApiRequest);

    // Only reset stateToFlush if the API call was successful
    stateToFlush = null;
  }

}
