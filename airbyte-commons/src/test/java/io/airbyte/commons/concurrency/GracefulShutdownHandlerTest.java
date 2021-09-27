/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import java.time.Duration;
import java.util.concurrent.ExecutorService;
import org.junit.jupiter.api.Test;

class GracefulShutdownHandlerTest {

  @Test
  public void testRun() throws InterruptedException {
    final ExecutorService executorService = mock(ExecutorService.class);
    final GracefulShutdownHandler gracefulShutdownHandler = new GracefulShutdownHandler(Duration.ofSeconds(30), executorService);
    gracefulShutdownHandler.start();
    gracefulShutdownHandler.join();

    verify(executorService).shutdown();
  }

}
