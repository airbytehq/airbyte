/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.util.concurrent;

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.stream.StreamStatusUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.ThreadPoolExecutor.AbortPolicy;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
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
public class ConcurrentStreamConsumer implements Consumer<Collection<AutoCloseableIterator<AirbyteMessage>>>, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConcurrentStreamConsumer.class);

  /**
   * Name of threads spawned by the {@link ConcurrentStreamConsumer}.
   */
  public static final String CONCURRENT_STREAM_THREAD_NAME = "concurrent-stream-thread";

  private final ExecutorService executorService;
  private final List<Exception> exceptions;
  private final Integer parallelism;
  private final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer;
  private final Optional<Consumer<AirbyteStreamStatusHolder>> streamStatusEmitter =
      Optional.of(AirbyteTraceMessageUtility::emitStreamStatusTrace);

  /**
   * Constructs a new {@link ConcurrentStreamConsumer} that will use the provided stream consumer to
   * execute each stream submitted to the {@link #accept(Collection<AutoCloseableIterator>)} method of
   * this consumer. Streams submitted to the {@link #accept(Collection<AutoCloseableIterator>)} method
   * will be converted to a {@link Runnable} and executed on an {@link ExecutorService} configured by
   * this consumer to ensure concurrent execution of each stream.
   *
   * @param streamConsumer The {@link Consumer} that accepts streams as an
   *        {@link AutoCloseableIterator}.
   * @param requestedParallelism The requested amount of parallelism that will be used as a hint to
   *        determine the appropriate number of threads to execute concurrently.
   */
  public ConcurrentStreamConsumer(final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer, final Integer requestedParallelism) {
    this.parallelism = computeParallelism(requestedParallelism);
    this.executorService = createExecutorService(parallelism);
    this.exceptions = new ArrayList<>();
    this.streamConsumer = streamConsumer;
  }

  @Override
  public void accept(final Collection<AutoCloseableIterator<AirbyteMessage>> streams) {
    /*
     * Submit the provided streams to the underlying executor service for concurrent execution. This
     * thread will track the status of each stream as well as consuming all messages produced from each
     * stream, passing them to the provided message consumer for further processing. Any exceptions
     * raised within the thread will be captured and exposed to the caller.
     */
    final Collection<CompletableFuture<Void>> futures = streams.stream()
        .map(stream -> new ConcurrentStreamRunnable(stream, this))
        .map(runnable -> CompletableFuture.runAsync(runnable, executorService))
        .collect(Collectors.toList());

    /*
     * Wait for the submitted streams to complete before returning. This uses the join() method to allow
     * all streams to complete even if one or more encounters an exception.
     */
    LOGGER.debug("Waiting for all streams to complete....");
    CompletableFuture.allOf(futures.toArray(new CompletableFuture[futures.size()])).join();
    LOGGER.debug("Completed consuming from all streams.");
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
   * Returns the parallelism value that will be used by this consumer to execute the consumption of
   * data from the provided streams in parallel.
   *
   * @return The parallelism value of this consumer.
   */
  public Integer getParallelism() {
    return computeParallelism(parallelism);
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
     * Selects the default thread pool size based on the provided value via an environment variable or
     * the number of available processors if the environment variable is not set/present. This is to
     * ensure that we do not over-parallelize unless requested explicitly.
     */
    final Integer defaultPoolSize = Optional.ofNullable(System.getenv("DEFAULT_CONCURRENT_STREAM_CONSUMER_THREADS"))
        .map(Integer::parseInt)
        .orElseGet(() -> Runtime.getRuntime().availableProcessors());
    LOGGER.debug("Default parallelism: {}, Requested parallelism: {}", defaultPoolSize, requestedParallelism);
    final Integer parallelism = Math.min(defaultPoolSize, requestedParallelism > 0 ? requestedParallelism : 1);
    LOGGER.debug("Computed concurrent stream consumer parallelism: {}", parallelism);
    return parallelism;
  }

  /**
   * Creates the {@link ExecutorService} that will be used by the consumer to consume from the
   * provided streams in parallel.
   *
   * @param nThreads The number of threads to execute concurrently.
   * @return The configured {@link ExecutorService}.
   */
  private ExecutorService createExecutorService(final Integer nThreads) {
    return new ThreadPoolExecutor(nThreads, nThreads, 0L, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<>(),
        new ConcurrentStreamThreadFactory(), new AbortPolicy());
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
      stream.getAirbyteStream().ifPresent(s -> LOGGER.error("Unable to consume from stream {}.", s, e));
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

  /**
   * Custom {@link ThreadFactory} that names the threads used to concurrently execute streams.
   */
  private static class ConcurrentStreamThreadFactory implements ThreadFactory {

    @Override
    public Thread newThread(final Runnable r) {
      final Thread thread = new Thread(r);
      if (r instanceof ConcurrentStreamRunnable) {
        final AutoCloseableIterator<AirbyteMessage> stream = ((ConcurrentStreamRunnable) r).stream();
        if (stream.getAirbyteStream().isPresent()) {
          final AirbyteStreamNameNamespacePair airbyteStream = stream.getAirbyteStream().get();
          thread.setName(String.format("%s-%s-%s", CONCURRENT_STREAM_THREAD_NAME, airbyteStream.getNamespace(), airbyteStream.getName()));
        } else {
          thread.setName(CONCURRENT_STREAM_THREAD_NAME);
        }
      } else {
        thread.setName(CONCURRENT_STREAM_THREAD_NAME);
      }
      return thread;
    }

  }

  /**
   * Custom {@link Runnable} that exposes the stream for thread naming purposes.
   *
   * @param stream The stream that is part of the {@link Runnable} execution.
   * @param consumer The {@link ConcurrentStreamConsumer} that will execute the stream.
   */
  private record ConcurrentStreamRunnable(AutoCloseableIterator<AirbyteMessage> stream, ConcurrentStreamConsumer consumer) implements Runnable {

    @Override
    public void run() {
      consumer.executeStream(stream);
    }

  }

}
