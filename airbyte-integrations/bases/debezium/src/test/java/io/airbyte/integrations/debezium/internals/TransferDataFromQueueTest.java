/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class TransferDataFromQueueTest {

  @Test
  public void test() throws InterruptedException {
    final LinkedBlockingQueue<Integer> sourceQueue = new LinkedBlockingQueue<>(10);
    final LinkedBlockingQueue<Integer> targetQueue = new LinkedBlockingQueue<>();
    final AtomicInteger recordsInserted = new AtomicInteger();
    final TransferDataFromQueue<Integer> transferDataFromQueue = new TransferDataFromQueue<>(sourceQueue, targetQueue,
        () -> recordsInserted.get() >= 99);
    final ExecutorService executorService = Executors.newSingleThreadExecutor();
    executorService.execute(() -> {
      for (int i = 0; i < 100; i++) {
        try {
          sourceQueue.put(i);
          recordsInserted.set(i);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }
      }
    });

    Thread.sleep(1000);
    executorService.shutdown();
    transferDataFromQueue.initiateTransfer();
    transferDataFromQueue.shutdown();

    Assertions.assertEquals(99, recordsInserted.get());
    Assertions.assertEquals(0, sourceQueue.size());
    Assertions.assertEquals(100, targetQueue.size());

    for (int i = 0; i < 99; i++) {
      Assertions.assertEquals(i, targetQueue.poll());
    }
  }

}
