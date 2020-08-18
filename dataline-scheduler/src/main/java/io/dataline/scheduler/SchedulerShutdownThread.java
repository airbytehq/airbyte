package io.dataline.scheduler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

public class SchedulerShutdownThread extends Thread {
  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerShutdownThread.class);
  private ExecutorService threadPool;

  public SchedulerShutdownThread(ExecutorService threadPool) {
    this.threadPool = threadPool;
  }

  @Override
  public void run() {
    threadPool.shutdown();

    try {
      if (!threadPool.awaitTermination(30, TimeUnit.SECONDS)) {
        LOGGER.error("Unable to kill worker threads by shutdown timeout.");
      }
    } catch (InterruptedException e) {
      LOGGER.error("Wait for graceful worker thread shutdown interrupted.", e);
    }
  }
}
