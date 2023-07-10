/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import io.airbyte.commons.util.AirbyteStreamAware;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import java.util.Optional;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility methods that support the generation of stream status updates.
 */
public class StreamStatusUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(StreamStatusUtils.class);

  /**
   * Creates a new {@link Consumer} that wraps the provided {@link Consumer} with stream status
   * reporting capabilities. Specifically, this consumer will emit an
   * {@link AirbyteStreamStatus#RUNNING} status after the first message is consumed by the delegated
   * {@link Consumer}.
   *
   * @param stream The stream from which the delegating {@link Consumer} will consume messages for
   *        processing.
   * @param delegateRecordCollector The delegated {@link Consumer} that will be called when this
   *        consumer accepts a message for processing.
   * @param streamStatusEmitter The optional {@link Consumer} that will be used to emit stream status
   *        updates.
   * @return A wrapping {@link Consumer} that provides stream status updates when the provided
   *         delegate {@link Consumer} is invoked.
   */
  public static Consumer<AirbyteMessage> statusTrackingRecordCollector(final AutoCloseableIterator<AirbyteMessage> stream,
                                                                       final Consumer<AirbyteMessage> delegateRecordCollector,
                                                                       final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter) {
    return new Consumer<>() {

      private boolean firstRead = true;

      @Override
      public void accept(final AirbyteMessage airbyteMessage) {
        try {
          delegateRecordCollector.accept(airbyteMessage);
        } finally {
          if (firstRead) {
            emitRunningStreamStatus(stream, streamStatusEmitter);
            firstRead = false;
          }
        }
      }

    };
  }

  /**
   * Emits a {@link AirbyteStreamStatus#RUNNING} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitRunningStreamStatus(final AutoCloseableIterator<AirbyteMessage> airbyteStream,
                                             final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    if (airbyteStream instanceof AirbyteStreamAware) {
      emitRunningStreamStatus((AirbyteStreamAware) airbyteStream, statusEmitter);
    }
  }

  /**
   * Emits a {@link AirbyteStreamStatus#RUNNING} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitRunningStreamStatus(final AirbyteStreamAware airbyteStream,
                                             final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    emitRunningStreamStatus(airbyteStream.getAirbyteStream(), statusEmitter);
  }

  /**
   * Emits a {@link AirbyteStreamStatus#RUNNING} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitRunningStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream,
                                             final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("RUNNING -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.RUNNING, statusEmitter);
    });
  }

  /**
   * Emits a {@link AirbyteStreamStatus#STARTED} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitStartStreamStatus(final AutoCloseableIterator<AirbyteMessage> airbyteStream,
                                           final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    if (airbyteStream instanceof AirbyteStreamAware) {
      emitStartStreamStatus((AirbyteStreamAware) airbyteStream, statusEmitter);
    }
  }

  /**
   * Emits a {@link AirbyteStreamStatus#STARTED} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitStartStreamStatus(final AirbyteStreamAware airbyteStream,
                                           final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    emitStartStreamStatus(airbyteStream.getAirbyteStream(), statusEmitter);
  }

  /**
   * Emits a {@link AirbyteStreamStatus#STARTED} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitStartStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream,
                                           final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("STARTING -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.STARTED, statusEmitter);
    });
  }

  /**
   * Emits a {@link AirbyteStreamStatus#COMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitCompleteStreamStatus(final AutoCloseableIterator<AirbyteMessage> airbyteStream,
                                              final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    if (airbyteStream instanceof AirbyteStreamAware) {
      emitCompleteStreamStatus((AirbyteStreamAware) airbyteStream, statusEmitter);
    }
  }

  /**
   * Emits a {@link AirbyteStreamStatus#COMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitCompleteStreamStatus(final AirbyteStreamAware airbyteStream,
                                              final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    emitCompleteStreamStatus(airbyteStream.getAirbyteStream(), statusEmitter);
  }

  /**
   * Emits a {@link AirbyteStreamStatus#COMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitCompleteStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream,
                                              final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("COMPLETE -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.COMPLETE, statusEmitter);
    });
  }

  /**
   * Emits a {@link AirbyteStreamStatus#INCOMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitIncompleteStreamStatus(final AutoCloseableIterator<AirbyteMessage> airbyteStream,
                                                final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    if (airbyteStream instanceof AirbyteStreamAware) {
      emitIncompleteStreamStatus((AirbyteStreamAware) airbyteStream, statusEmitter);
    }
  }

  /**
   * Emits a {@link AirbyteStreamStatus#INCOMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitIncompleteStreamStatus(final AirbyteStreamAware airbyteStream,
                                                final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    emitIncompleteStreamStatus(airbyteStream.getAirbyteStream(), statusEmitter);
  }

  /**
   * Emits a {@link AirbyteStreamStatus#INCOMPLETE} stream status for the provided stream.
   *
   * @param airbyteStream The stream that should be associated with the stream status.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  public static void emitIncompleteStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream,
                                                final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("INCOMPLETE -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.INCOMPLETE, statusEmitter);
    });
  }

  /**
   * Emits a stream status for the provided stream.
   *
   * @param airbyteStreamNameNamespacePair The stream identifier.
   * @param airbyteStreamStatus The status update.
   * @param statusEmitter The {@link Optional} stream status emitter.
   */
  private static void emitStreamStatus(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                       final AirbyteStreamStatus airbyteStreamStatus,
                                       final Optional<Consumer<AirbyteStreamStatusHolder>> statusEmitter) {
    statusEmitter.ifPresent(consumer -> consumer.accept(new AirbyteStreamStatusHolder(airbyteStreamNameNamespacePair, airbyteStreamStatus)));
  }

}
