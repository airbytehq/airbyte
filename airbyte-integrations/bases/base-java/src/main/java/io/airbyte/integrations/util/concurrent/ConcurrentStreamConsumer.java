/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util.concurrent;

import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.stream.StreamStatusUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * {@link Consumer} implementation that consumes {@link AirbyteMessage} records from each provided
 * stream concurrently.
 * <p>
 * </p>
 * The consumer calculates the parallelism based on the provided requested parallelism. If the
 * requested parallelism is greater than zero, the minimum value between the requested parallelism
 * and the maximum number of allowed threads is chosen as the parallelism value. Otherwise, the
 * minimum parallelism value is selected. This is to avoid issues with attempting to execute with a
 * parallelism value of zero, which is not allowed by the underlying {@link ExecutorService}.
 * <p>
 * </p>
 * This consumer will capture any raised exceptions during execution of each stream. Anu exceptions
 * are stored and made available by calling the {@link #getException()} method.
 */
public class ConcurrentStreamConsumer implements Consumer<AutoCloseableIterator<AirbyteMessage>>, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConcurrentStreamConsumer.class);

  private final ExecutorService executorService;
  private final List<Exception> exceptions;
  private final Collection<CompletableFuture> futures;
  private final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer;
  private final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter = Optional.of(AirbyteTraceMessageUtility::emitStreamStatusTrace);

  public ConcurrentStreamConsumer(final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer, final Integer requestedParallelism) {
    this.executorService = Executors.newFixedThreadPool(computeParallelism(requestedParallelism));
    this.exceptions = new ArrayList<>();
    this.futures = new ArrayList<>();
    this.streamConsumer = streamConsumer;
  }

  @Override
  public void accept(final AutoCloseableIterator<AirbyteMessage> stream) {
    /*
     * Submit the provided stream to the underlying executor service for concurrent execution. This
     * thread will track the stream's status as well as consuming all messages produced from the stream,
     * passing them to the provided message consumer for further processing. Any exceptions raised
     * within the thread will be captured and exposed to the caller.
     */
    futures.add(CompletableFuture.runAsync(() -> executeStream(stream), executorService));
  }

  /**
   * Returns the first captured {@link Exception}.
   *
   * @return The first captured {@link Exception} or an empty {@link Optional} if no exceptions were
   *         captured during execution.
   */
  public Optional<Exception> getException() {
    if (!exceptions.isEmpty()) {
      return Optional.of(exceptions.get(0));
    } else {
      return Optional.empty();
    }
  }

  /**
   * Returns the list of exceptions captured during execution of the streams, if any.
   *
   * @return The collection of captured exceptions or an empty list.
   */
  public List<Exception> getExceptions() {
    return Collections.unmodifiableList(exceptions);
  }

  /**
   * Waits for each submitted stream to complete execution.
   *
   * @throws ExecutionException if unable to wait for the execution to complete.
   * @throws InterruptedException if the wait for the exectuion to complete is interrupted.
   */
  public void waitFor() throws ExecutionException, InterruptedException {
    // Wait for all threads to run before closing
    if (!futures.isEmpty()) {
      CompletableFuture.allOf(futures.toArray(new CompletableFuture[futures.size()])).get();
    }
  }

  /**
   * Calculates the parallelism based on the requested parallelism. If the requested parallelism is
   * greater than zero, the minimum value between the parallelism and the maximum parallelism is
   * chosen as the parallelism count. Otherwise, the minimum parallelism is selected. This is to avoid
   * issues with attempting to create an executor service with a thread pool size of 0, which is not
   * allowed.
   *
   * @param requestedParallelism The requested parallelism.
   * @return The selected parallelism based on the factors outlined above.
   */
  private Integer computeParallelism(final Integer requestedParallelism) {
    /*
     * TODO What is the correct upper bound here? It should probably be provided by the code that
     * creates this iterator to account for the different types of connectors and their limitations. For
     * instance, a JDBC-based source connector should probably set the "MAX_THREADS" to the maximum
     * number of connections in the database connection pool used by the source. For API-based source
     * connectors, this should be the maximum number of concurrent connections from one host/IP address
     * that the API supports.
     */
    final Integer parallelism = Math.min(10, requestedParallelism > 0 ? requestedParallelism : 1);
    LOGGER.debug("Computed concurrent stream parallelism: {}", parallelism);
    return parallelism;
  }

  /**
   * Executes the stream by providing it to the configured {@link #streamConsumer}.
   *
   * @param stream The stream to be executed.
   */
  private void executeStream(final AutoCloseableIterator<AirbyteMessage> stream) {
    try (stream) {
      stream.getAirbyteStream().ifPresent(s -> LOGGER.debug("Consuming from stream {}...", s));
      StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter);
      streamConsumer.accept(stream);
      StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter);
      stream.getAirbyteStream().ifPresent(s -> LOGGER.debug("Consumption from stream {} complete.", s));
    } catch (final Exception e) {
      stream.getAirbyteStream().ifPresent(s -> LOGGER.error("Unable to consume from stream {}.", s));
      StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter);
      exceptions.add(e);
    }
  }

  @Override
  public void close() throws Exception {
    // Block waiting for the executor service to close
    executorService.shutdownNow();
    executorService.awaitTermination(30, TimeUnit.SECONDS);
  }

}
