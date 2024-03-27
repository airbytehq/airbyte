/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.lang.MoreBooleans;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class has the logic for shutting down Debezium Engine in graceful manner. We made it Generic
 * to allow us to write tests easily.
 */
public class DebeziumShutdownProcedure<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumShutdownProcedure.class);
  private final LinkedBlockingQueue<T> sourceQueue;
  private final LinkedBlockingQueue<T> targetQueue;
  private final ExecutorService executorService;
  private final Supplier<Boolean> publisherStatusSupplier;
  private final VoidCallable debeziumThreadRequestClose;
  private Throwable exception;
  private boolean hasTransferThreadShutdown;

  public DebeziumShutdownProcedure(final LinkedBlockingQueue<T> sourceQueue,
                                   final VoidCallable debeziumThreadRequestClose,
                                   final Supplier<Boolean> publisherStatusSupplier) {
    this.sourceQueue = sourceQueue;
    this.targetQueue = new LinkedBlockingQueue<>();
    this.debeziumThreadRequestClose = debeziumThreadRequestClose;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.hasTransferThreadShutdown = false;
    this.executorService = Executors.newSingleThreadExecutor(r -> {
      final Thread thread = new Thread(r, "queue-data-transfer-thread");
      thread.setUncaughtExceptionHandler((t, e) -> {
        exception = e;
      });
      return thread;
    });
  }

  private Runnable transfer() {
    return () -> {
      while (!sourceQueue.isEmpty() || !hasEngineShutDown()) {
        try {
          final T event = sourceQueue.poll(100, TimeUnit.MILLISECONDS);
          if (event != null) {
            targetQueue.put(event);
          }
        } catch (final InterruptedException e) {
          Thread.currentThread().interrupt();
          throw new RuntimeException(e);
        }
      }
    };
  }

  private boolean hasEngineShutDown() {
    return MoreBooleans.isTruthy(publisherStatusSupplier.get());
  }

  private void initiateTransfer() {
    executorService.execute(transfer());
  }

  public LinkedBlockingQueue<T> getRecordsRemainingAfterShutdown() {
    if (!hasTransferThreadShutdown) {
      LOGGER.warn("Queue transfer thread has not shut down, some records might be missing.");
    }
    return targetQueue;
  }

  /**
   * This method triggers the shutdown of Debezium Engine. When we trigger Debezium shutdown, the main
   * thread pauses, as a result we stop reading data from the {@link sourceQueue} and since the queue
   * is of fixed size, if it's already at capacity, Debezium won't be able to put remaining records in
   * the queue. So before we trigger Debezium shutdown, we initiate a transfer of the records from the
   * {@link sourceQueue} to a new queue i.e. {@link targetQueue}. This allows Debezium to continue to
   * put records in the {@link sourceQueue} and once done, gracefully shutdown. After the shutdown is
   * complete we just have to read the remaining records from the {@link targetQueue}
   */
  public void initiateShutdownProcedure() {
    if (hasEngineShutDown()) {
      LOGGER.info("Debezium Engine has already shut down.");
      return;
    }
    Exception exceptionDuringEngineClose = null;
    try {
      initiateTransfer();
      debeziumThreadRequestClose.call();
    } catch (final Exception e) {
      exceptionDuringEngineClose = e;
      throw new RuntimeException(e);
    } finally {
      try {
        shutdownTransferThread();
      } catch (final Exception e) {
        if (exceptionDuringEngineClose != null) {
          e.addSuppressed(exceptionDuringEngineClose);
          throw e;
        }
      }
    }
  }

  private void shutdownTransferThread() {
    executorService.shutdown();
    boolean terminated = false;
    while (!terminated) {
      try {
        terminated = executorService.awaitTermination(5, TimeUnit.MINUTES);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new RuntimeException(e);
      }
    }
    hasTransferThreadShutdown = true;
    if (exception != null) {
      throw new RuntimeException(exception);
    }
  }

}
