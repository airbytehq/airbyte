/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.util.AirbyteStreamAware;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import java.util.Optional;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * Test suite for the {@link StreamStatusUtils} class.
 */
@ExtendWith(MockitoExtension.class)
class StreamStatusUtilsTest {

  private static final String NAME = "name";
  private static final String NAMESPACE = "namespace";

  @Captor
  private ArgumentCaptor<AirbyteStreamStatusHolder> airbyteStreamStatusHolderArgumentCaptor;

  @Test
  void testCreateStreamStatusConsumerWrapper() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();
    final Consumer<AirbyteMessage> messageConsumer = mock(Consumer.class);

    final Consumer<AirbyteMessage> wrappedMessageConsumer =
        StreamStatusUtils.statusTrackingRecordCollector(stream, messageConsumer, streamStatusEmitter);

    assertNotEquals(messageConsumer, wrappedMessageConsumer);
  }

  @Test
  void testStreamStatusConsumerWrapperProduceStreamStatus() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);
    final Consumer<AirbyteMessage> messageConsumer = mock(Consumer.class);
    final AirbyteMessage airbyteMessage = mock(AirbyteMessage.class);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    final Consumer<AirbyteMessage> wrappedMessageConsumer =
        StreamStatusUtils.statusTrackingRecordCollector(stream, messageConsumer, streamStatusEmitter);

    assertNotEquals(messageConsumer, wrappedMessageConsumer);

    wrappedMessageConsumer.accept(airbyteMessage);
    wrappedMessageConsumer.accept(airbyteMessage);
    wrappedMessageConsumer.accept(airbyteMessage);

    verify(messageConsumer, times(3)).accept(any());
    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.RUNNING, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitRunningStreamStatusIterator() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.RUNNING, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitRunningStreamStatusIteratorEmptyAirbyteStream() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitRunningStreamStatusIteratorEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitRunningStreamStatusAirbyteStreamAware() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.RUNNING, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitRunningStreamStatusAirbyteStreamAwareEmptyStream() {
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitRunningStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitRunningStreamStatusAirbyteStream() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    StreamStatusUtils.emitRunningStreamStatus(Optional.of(airbyteStream), streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.RUNNING, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitRunningStreamStatusEmptyAirbyteStream() {
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(Optional.empty(), streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitRunningStreamStatusAirbyteStreamEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    assertDoesNotThrow(() -> StreamStatusUtils.emitRunningStreamStatus(Optional.of(airbyteStream), streamStatusEmitter));
  }

  @Test
  void testEmitStartedStreamStatusIterator() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.STARTED, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitStartedStreamStatusIteratorEmptyAirbyteStream() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitStartedStreamStatusIteratorEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitStartedStreamStatusAirbyteStreamAware() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.STARTED, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitStartedStreamStatusAirbyteStreamAwareEmptyStream() {
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitStartedStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitStartedStreamStatusAirbyteStream() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    StreamStatusUtils.emitStartStreamStatus(Optional.of(airbyteStream), streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.STARTED, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitStartedStreamStatusEmptyAirbyteStream() {
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(Optional.empty(), streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitStartedStreamStatusAirbyteStreamEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    assertDoesNotThrow(() -> StreamStatusUtils.emitStartStreamStatus(Optional.of(airbyteStream), streamStatusEmitter));
  }

  @Test
  void testEmitCompleteStreamStatusIterator() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.COMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitCompleteStreamStatusIteratorEmptyAirbyteStream() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitCompleteStreamStatusIteratorEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitCompleteStreamStatusAirbyteStreamAware() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.COMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitCompleteStreamStatusAirbyteStreamAwareEmptyStream() {
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitCompleteStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitCompleteStreamStatusAirbyteStream() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    StreamStatusUtils.emitCompleteStreamStatus(Optional.of(airbyteStream), streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.COMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitCompleteStreamStatusEmptyAirbyteStream() {
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(Optional.empty(), streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitCompleteStreamStatusAirbyteStreamEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    assertDoesNotThrow(() -> StreamStatusUtils.emitCompleteStreamStatus(Optional.of(airbyteStream), streamStatusEmitter));
  }

  @Test
  void testEmitIncompleteStreamStatusIterator() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.INCOMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitIncompleteStreamStatusIteratorEmptyAirbyteStream() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitIncompleteStreamStatusIteratorEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitIncompleteStreamStatusAirbyteStreamAware() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.INCOMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitIncompleteStreamStatusAirbyteStreamAwareEmptyStream() {
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    when(stream.getAirbyteStream()).thenReturn(Optional.empty());

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitIncompleteStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final AirbyteStreamAware stream = mock(AirbyteStreamAware.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    when(stream.getAirbyteStream()).thenReturn(Optional.of(airbyteStream));

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter));
  }

  @Test
  void testEmitIncompleteStreamStatusAirbyteStream() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    StreamStatusUtils.emitIncompleteStreamStatus(Optional.of(airbyteStream), streamStatusEmitter);

    verify(statusEmitter, times(1)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
    assertEquals(AirbyteStreamStatus.INCOMPLETE, airbyteStreamStatusHolderArgumentCaptor.getValue().toTraceMessage().getStreamStatus().getStatus());
  }

  @Test
  void testEmitIncompleteStreamStatusEmptyAirbyteStream() {
    final Consumer<AirbyteStreamStatusHolder> statusEmitter = mock(Consumer.class);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(statusEmitter);

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(Optional.empty(), streamStatusEmitter));
    verify(statusEmitter, times(0)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
  }

  @Test
  void testEmitIncompleteStreamStatusAirbyteStreamEmptyStatusEmitter() {
    final AirbyteStreamNameNamespacePair airbyteStream = new AirbyteStreamNameNamespacePair(NAME, NAMESPACE);
    final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.empty();

    assertDoesNotThrow(() -> StreamStatusUtils.emitIncompleteStreamStatus(Optional.of(airbyteStream), streamStatusEmitter));
  }

}
