/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.airbyte.commons.lang.MoreBooleans;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public class TransferDataFromQueue<T> implements Runnable {

  private final LinkedBlockingQueue<T> sourceQueue;
  private final LinkedBlockingQueue<T> targetQueue;
  private final ExecutorService executorService;
  private final Supplier<Boolean> publisherStatusSupplier;
  private Throwable exception;

  public TransferDataFromQueue(final LinkedBlockingQueue<T> sourceQueue,
                               final LinkedBlockingQueue<T> targetQueue,
                               final Supplier<Boolean> publisherStatusSupplier) {
    this.sourceQueue = sourceQueue;
    this.targetQueue = targetQueue;
    this.publisherStatusSupplier = publisherStatusSupplier;
    this.executorService = Executors.newSingleThreadExecutor(r -> {
      final Thread thread = new Thread(r, "queue-data-transfer-thread");
      thread.setUncaughtExceptionHandler((t, e) -> {
        exception = e;
      });
      return thread;
    });
  }

  @Override
  public void run() {
    while (!sourceQueue.isEmpty() || !MoreBooleans.isTruthy(publisherStatusSupplier.get())) {
      try {
        T event = sourceQueue.poll(10, TimeUnit.SECONDS);
        if (event != null) {
          targetQueue.put(event);
        }
      } catch (final InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new RuntimeException(e);
      }
    }
  }

  public void initiateTransfer() {
    executorService.execute(this);
  }

  public void shutdown() {
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

    if (exception != null) {
      throw new RuntimeException(exception);
    }
  }

}
