/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Custom {@link AbstractIterator} implementation that provides iteration over a set of iterators in
 * parallel.
 * <p>
 * </p>
 * This iterator submits each iterator in the set of iterators to a thread pool, which fetches data
 * from each iterator in parallel up to a parallelism limit. Results are offered to an internal
 * queue, which is drained by the main {@link #next()} method implemented by this iterator. Note
 * that the {@link #next()} method call will block indefinitely waiting for data to become available
 * on the internal queue, provided that the iterator itself has not been closed or finished.
 * <p>
 * </p>
 * The iterator is considered to be finished if there are no underlying iterators to read from
 * <b>OR</b> if all underlying iterators have finished reading data and have signaled that they have
 * finished.
 * <p>
 * </p>
 * This iterator will also report stream status as it processes the underlying iterators for each
 * iterator that implements the {@link AirbyteStreamAware} interface.
 *
 * @param <T> The type of data returned by a call to {@link #next()} on the iterator and all
 *        underlying iterators.
 */
public final class ParallelCompositeIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T>, AirbyteStreamAware {

  private static final Logger LOGGER = LoggerFactory.getLogger(ParallelCompositeIterator.class);
  private static final Integer MAX_CAPACITY = 1000;
  private static final Integer MAX_THREADS = 10;
  private static final Integer MIN_THREADS = 1;

  private final Optional<Consumer<AirbyteStreamStatusHolder>> airbyteStreamStatusConsumer;
  private final ExecutorService executorService;
  private boolean hasClosed;
  private final BlockingQueue<InternalMessage<T>> internalQueue;
  private final Set<AutoCloseableIterator<T>> iterators;
  private boolean started = false;
  private int closedCount = 0;

  ParallelCompositeIterator(final Collection<AutoCloseableIterator<T>> iterators,
                            final Consumer<AirbyteStreamStatusHolder> airbyteStreamStatusConsumer) {
    this.airbyteStreamStatusConsumer = Optional.ofNullable(airbyteStreamStatusConsumer);
    this.iterators = iterators != null ? new HashSet<>(iterators) : new HashSet<>();
    /*
     * TODO What is the correct upper bound here? It should probably be provided by the code that
     * creates this iterator to account for the different types of connectors and their limitations. For
     * instance, a JDBC-based source connector should probably set the "MAX_THREADS" to the maximum
     * number of connections in the database connection pool used by the source. For API-based source
     * connectors, this should be the maximum number of concurrent connections from one host/IP address
     * that the API supports.
     */
    executorService = Executors.newFixedThreadPool(computeThreadPoolSize());
    /*
     * TODO Expose the max capacity as an advanced connector setting. This would allow the end user to
     * configure the trade-off between throughput and resource usage (memory to handle the messages on
     * the queue). Records may have arbitrary sizes requiring this value to be tweaked based on the
     * shape of the data being read.
     */
    internalQueue = new LinkedBlockingQueue<>(MAX_CAPACITY);
    this.hasClosed = false;
  }

  /**
   * Starts the parallel processing of the underlying iterators by submitting each iterator to the
   * internal thread pool. If the iterator has already started parallel processing, the call to this
   * method will be ignored.
   */
  public void start() {
    if (!started) {
      LOGGER.debug("Starting parallel consumption of streams...");
      iterators.forEach(iterator -> {
        executorService.submit(() -> consumeFromStream(iterator));
      });
      started = true;
      LOGGER.debug("Parallel stream consumption started.");
    } else {
      LOGGER.debug("Parallel stream consumption already started.");
    }
  }

  @Override
  protected T computeNext() {
    try {
      assertHasNotClosed();

      if (!started) {
        start();
      }

      if (iterators.isEmpty()) {
        return endOfData();
      }

      // Block while waiting for the next result to be available
      final T result = internalQueue.take().data();
      LOGGER.debug("Fetched next result {} from internal queue.", result);

      // If the result is null, that means all streams have finished producing results.
      return result != null ? result : endOfData();
    } catch (final InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    hasClosed = true;

    final List<Exception> exceptions = new ArrayList<>();
    for (final AutoCloseableIterator<T> iterator : iterators) {
      try {
        iterator.close();
      } catch (final Exception e) {
        LOGGER.error("exception while closing", e);
        exceptions.add(e);
      }
    }

    if (!exceptions.isEmpty()) {
      throw exceptions.get(0);
    }

    // Block waiting for the executor service to close
    executorService.shutdownNow();
    executorService.awaitTermination(30, TimeUnit.SECONDS);
  }

  @Override
  public Optional<AirbyteStreamNameNamespacePair> getAirbyteStream() {
    return AirbyteStreamAware.super.getAirbyteStream();
  }

  private void assertHasNotClosed() {
    Preconditions.checkState(!hasClosed);
  }

  /**
   * Consumes all available messages from the provided iterator, putting each message on the internal
   * queue.
   *
   * @param iterator An {@link AutoCloseableIterator} implementation.
   */
  private void consumeFromStream(final AutoCloseableIterator<T> iterator) {
    boolean firstRead = true;
    final Optional<AirbyteStreamNameNamespacePair> stream = getStream(iterator);
    emitStartStreamStatus(stream);

    try (iterator) {
      while (iterator.hasNext()) {
        final T next = iterator.next();
        LOGGER.debug("Writing data '{}' for stream {}...", next, stream.orElse(null));
        internalQueue.put(new InternalMessage(next));
        if (firstRead) {
          emitRunningStreamStatus(stream);
          firstRead = false;
        }
      }

      emitCompleteStreamStatus(stream);
    } catch (final Exception e) {
      LOGGER.error("Unable to read data from stream {}.", stream.orElse(null), e);
      emitIncompleteStreamStatus(stream);
    } finally {
      // Mark the stream as done
      onEndOfStream(stream);
    }
  }

  /**
   * Calculates the thread pool size based on the number of streams, as represented by the size of the
   * iterator list maintained by this iterator. If the iterators list is not empty, the minimum value
   * between the number of iterators and the maximum number of allowed threads is chosen as the thread
   * pool size. Otherwise, the minimum thread pool size is selected. This is to avoid issues with
   * attempting to create an executor service with a thread pool size of 0, which is not allowed.
   *
   * @return The thread pool size.
   */
  private Integer computeThreadPoolSize() {
    return Math.min(MAX_THREADS, (iterators.isEmpty() ? MIN_THREADS : iterators.size()));
  }

  /**
   * Callback method that handles the end of each stream processed in parallel by this iterator.
   * <p>
   * </p>
   * When all streams have called this callback, an end of processing message ({@code null}) is
   * published to the internal queue to signal the iterator that it has reached the end of iteration.
   *
   * @param airbyteStream The current stream identifier, if present.
   */
  private void onEndOfStream(final Optional<AirbyteStreamNameNamespacePair> airbyteStream) {
    LOGGER.debug("Handling completion of stream {}...", airbyteStream.orElse(null));
    closedCount++;
    if (closedCount == iterators.size()) {
      // Send a poison pill message to end the iterator
      internalQueue.offer(new InternalMessage<>(null));
    }
  }

  private void emitRunningStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("RUNNING -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.RUNNING);
    });
  }

  private void emitStartStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("STARTING -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.STARTED);
    });
  }

  private void emitCompleteStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("COMPLETE -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.COMPLETE);
    });
  }

  private void emitIncompleteStreamStatus(final Optional<AirbyteStreamNameNamespacePair> airbyteStream) {
    airbyteStream.ifPresent(s -> {
      LOGGER.debug("COMPLETE -> {}", s);
      emitStreamStatus(s, AirbyteStreamStatus.INCOMPLETE);
    });
  }

  private void emitStreamStatus(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                final AirbyteStreamStatus airbyteStreamStatus) {
    airbyteStreamStatusConsumer.ifPresent(c -> c.accept(new AirbyteStreamStatusHolder(airbyteStreamNameNamespacePair, airbyteStreamStatus)));
  }

  private Optional<AirbyteStreamNameNamespacePair> getStream(final AutoCloseableIterator<T> iterator) {
    if (iterator instanceof AirbyteStreamAware) {
      return AirbyteStreamAware.class.cast(iterator).getAirbyteStream();
    } else {
      return Optional.empty();
    }
  }

  /**
   * Wrapper record for use on the internal queue so that a poison message ({@code nul}) can be
   * offered to the queue to mark the end of all streams parallelized by this iterator.
   *
   * @param data The data to be returned by the call to this iterator's {@link #next()} method.
   * @param <T> The type of data returned by a call to {@link #next()} on the iterator and all
   *        underlying iterators.
   */
  private record InternalMessage<T> (T data) {}

}
