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

public class DebeziumShutdownProcedureTest {

  @Test
  public void test() throws InterruptedException {
    final LinkedBlockingQueue<Integer> sourceQueue = new LinkedBlockingQueue<>(10);
    final AtomicInteger recordsInserted = new AtomicInteger();
    final ExecutorService executorService = Executors.newSingleThreadExecutor();
    final DebeziumShutdownProcedure<Integer> debeziumShutdownProcedure = new DebeziumShutdownProcedure<>(sourceQueue,
        executorService::shutdown, () -> recordsInserted.get() >= 99);
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
    debeziumShutdownProcedure.initiateShutdownProcedure();

    Assertions.assertEquals(99, recordsInserted.get());
    Assertions.assertEquals(0, sourceQueue.size());
    Assertions.assertEquals(100, debeziumShutdownProcedure.getRecordsRemainingAfterShutdown().size());

    for (int i = 0; i < 100; i++) {
      Assertions.assertEquals(i, debeziumShutdownProcedure.getRecordsRemainingAfterShutdown().poll());
    }
  }

}
