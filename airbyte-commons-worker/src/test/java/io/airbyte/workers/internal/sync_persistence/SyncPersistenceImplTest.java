/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.sync_persistence;

import static io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType.STREAM;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.clearInvocations;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.api.client.model.generated.ConnectionStateType;
import io.airbyte.api.client.model.generated.StreamState;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.workers.internal.state_aggregator.StateAggregatorFactory;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import org.assertj.core.api.CollectionAssert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class SyncPersistenceImplTest {

  private final long FLUSH_PERIOD = 60;

  private SyncPersistenceImpl syncPersistence;
  private StateApi stateApi;
  private ScheduledExecutorService executorService;
  private ArgumentCaptor<Runnable> actualFlushMethod;

  private UUID connectionId;

  @BeforeEach
  void beforeEach() {
    connectionId = UUID.randomUUID();

    // Setting up an ArgumentCaptor to be able to manually trigger the actual flush method rather than
    // relying on the ScheduledExecutorService and having to deal with Thread.sleep in the tests.
    actualFlushMethod = ArgumentCaptor.forClass(Runnable.class);

    // Wire the executor service with arg captures
    executorService = mock(ScheduledExecutorService.class);
    when(executorService.scheduleAtFixedRate(actualFlushMethod.capture(), eq(0L), eq(FLUSH_PERIOD), eq(TimeUnit.SECONDS)))
        .thenReturn(mock(ScheduledFuture.class));

    // Setting syncPersistence
    stateApi = mock(StateApi.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    when(featureFlags.useStreamCapableState()).thenReturn(true);
    syncPersistence = new SyncPersistenceImpl(connectionId, stateApi, new StateAggregatorFactory(featureFlags), executorService, FLUSH_PERIOD);
  }

  @AfterEach
  void afterEach() {
    syncPersistence.close();
  }

  @Test
  void testPersistHappyPath() throws ApiException {
    final AirbyteStateMessage stateA1 = getStreamState("A", 1);
    syncPersistence.persist(stateA1);
    verify(executorService).scheduleAtFixedRate(any(Runnable.class), eq(0L), eq(FLUSH_PERIOD), eq(TimeUnit.SECONDS));
    clearInvocations(executorService);

    // Simulating the expected flush execution
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateA1));
    clearInvocations(stateApi);

    final AirbyteStateMessage stateB1 = getStreamState("B", 1);
    final AirbyteStateMessage stateC2 = getStreamState("C", 2);
    syncPersistence.persist(stateB1);
    syncPersistence.persist(stateC2);

    // Forcing a second flush
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateB1, stateC2));
    clearInvocations(stateApi);

    // Forcing another flush without data to flush
    actualFlushMethod.getValue().run();
    verify(stateApi, never()).createOrUpdateState(any());
    clearInvocations(stateApi);

    // scheduleAtFixedRate should not have received any other calls
    verify(executorService, never()).scheduleAtFixedRate(any(), anyLong(), anyLong(), any());
  }

  @Test
  void testPersistWithApiFailures() throws ApiException {
    final AirbyteStateMessage stateF1 = getStreamState("F", 1);
    syncPersistence.persist(stateF1);

    // Set API call to fail
    when(stateApi.createOrUpdateState(any())).thenThrow(new ApiException());

    // Flushing
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateF1));
    clearInvocations(stateApi);

    // Adding more states
    final AirbyteStateMessage stateG1 = getStreamState("G", 1);
    syncPersistence.persist(stateG1);

    // Flushing again
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateF1, stateG1));
    clearInvocations(stateApi);

    // Adding more states
    final AirbyteStateMessage stateF2 = getStreamState("F", 2);
    syncPersistence.persist(stateF2);

    // Flushing again
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateF2, stateG1));
    clearInvocations(stateApi);

    // Clear the error state from the API
    reset(stateApi);

    // Flushing again
    actualFlushMethod.getValue().run();
    verifyStateUpdateApiCall(List.of(stateF2, stateG1));
    clearInvocations(stateApi);

    // Sanity check Flushing again should not trigger an API call since all the data has been
    // successfully flushed
    actualFlushMethod.getValue().run();
    verify(stateApi, never()).createOrUpdateState(any());
  }

  @Test
  void testClose() throws InterruptedException, ApiException {
    // Adding a state to flush, this state should get flushed when we close syncPersistence
    final AirbyteStateMessage stateA2 = getStreamState("A", 2);
    syncPersistence.persist(stateA2);

    // Shutdown, we expect the executor service to be stopped and an stateApi to be called
    when(executorService.awaitTermination(anyLong(), any())).thenReturn(true);
    syncPersistence.close();
    verify(executorService).shutdown();
    verifyStateUpdateApiCall(List.of(stateA2));
  }

  @Test
  void testCloseMergeStatesFromPreviousFailure() throws ApiException, InterruptedException {
    // Adding a state to flush, this state should get flushed when we close syncPersistence
    final AirbyteStateMessage stateA2 = getStreamState("closeA", 2);
    syncPersistence.persist(stateA2);

    // Trigger a failure
    when(stateApi.createOrUpdateState(any())).thenThrow(new ApiException());
    actualFlushMethod.getValue().run();

    final AirbyteStateMessage stateB1 = getStreamState("closeB", 1);
    syncPersistence.persist(stateB1);

    // Final flush
    reset(stateApi);
    when(executorService.awaitTermination(anyLong(), any())).thenReturn(true);
    syncPersistence.close();
    verifyStateUpdateApiCall(List.of(stateA2, stateB1));
  }

  @Test
  void testCloseShouldAttemptToRetryFinalFlush() throws ApiException, InterruptedException {
    final AirbyteStateMessage state = getStreamState("final retry", 2);
    syncPersistence.persist(state);

    // Setup some API failures
    when(stateApi.createOrUpdateState(any()))
        .thenThrow(new ApiException())
        .thenReturn(mock(ConnectionState.class));

    // Final flush
    when(executorService.awaitTermination(anyLong(), any())).thenReturn(true);
    syncPersistence.close();
    verify(stateApi, times(2)).createOrUpdateState(buildStateRequest(connectionId, List.of(state)));
  }

  @Test
  void testCloseWhenFailBecauseFlushTookTooLong() throws InterruptedException, ApiException {
    syncPersistence.persist(getStreamState("oops", 42));

    // Simulates a flush taking too long to terminate
    when(executorService.awaitTermination(anyLong(), any())).thenReturn(false);

    syncPersistence.close();
    verify(executorService).shutdown();
    // Since the previous write has an unknown state, we do not attempt to persist after the close
    verify(stateApi, never()).createOrUpdateState(any());
  }

  @Test
  void testCloseWhenFailBecauseThreadInterrupted() throws InterruptedException, ApiException {
    syncPersistence.persist(getStreamState("oops", 42));

    // Simulates a flush taking too long to terminate
    when(executorService.awaitTermination(anyLong(), any())).thenThrow(new InterruptedException());

    syncPersistence.close();
    verify(executorService).shutdown();
    // Since the previous write has an unknown state, we do not attempt to persist after the close
    verify(stateApi, never()).createOrUpdateState(any());
  }

  @Test
  void testCloseWithPendingFlushShouldCallTheApi() throws InterruptedException, ApiException {
    // Shutdown, we expect the executor service to be stopped and an stateApi to be called
    when(executorService.awaitTermination(anyLong(), any())).thenReturn(true);
    syncPersistence.close();
    verify(executorService).shutdown();
    verify(stateApi, never()).createOrUpdateState(any());
  }

  private void verifyStateUpdateApiCall(final List<AirbyteStateMessage> expectedStateMessages) {
    // Using an ArgumentCaptor because we do not have an ordering constraint on the states, so we need
    // to add an unordered collection equals
    final ArgumentCaptor<ConnectionStateCreateOrUpdate> captor = ArgumentCaptor.forClass(ConnectionStateCreateOrUpdate.class);

    try {
      verify(stateApi).createOrUpdateState(captor.capture());
    } catch (ApiException e) {
      throw new RuntimeException(e);
    }
    final ConnectionStateCreateOrUpdate actual = captor.getValue();
    final ConnectionStateCreateOrUpdate expected = buildStateRequest(connectionId, expectedStateMessages);

    // Checking the stream states
    CollectionAssert.assertThatCollection(actual.getConnectionState().getStreamState())
        .containsExactlyInAnyOrderElementsOf(expected.getConnectionState().getStreamState());

    // Checking the rest of the payload
    actual.getConnectionState().setStreamState(List.of());
    expected.getConnectionState().setStreamState(List.of());
    assertEquals(expected, actual);
  }

  private ConnectionStateCreateOrUpdate buildStateRequest(final UUID connectionId, final List<AirbyteStateMessage> stateMessages) {
    return new ConnectionStateCreateOrUpdate()
        .connectionId(connectionId)
        .connectionState(new ConnectionState()
            .connectionId(connectionId)
            .stateType(ConnectionStateType.STREAM)
            .streamState(
                stateMessages.stream().map(s -> new StreamState()
                    .streamDescriptor(
                        new io.airbyte.api.client.model.generated.StreamDescriptor().name(s.getStream().getStreamDescriptor().getName()))
                    .streamState(s.getStream().getStreamState())).toList()));
  }

  private AirbyteStateMessage getStreamState(final String streamName, final int stateValue) {
    return new AirbyteStateMessage().withType(STREAM)
        .withStream(
            new AirbyteStreamState()
                .withStreamDescriptor(
                    new StreamDescriptor()
                        .withName(streamName))
                .withStreamState(Jsons.jsonNode(stateValue)));
  }

}
