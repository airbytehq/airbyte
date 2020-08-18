package io.dataline.scheduler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

public class SchedulerShutdownHandler extends Thread {
  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerShutdownHandler.class);
  private ExecutorService[] threadPools;

  public SchedulerShutdownHandler(ExecutorService... threadPools) {
    this.threadPools = threadPools;
  }

  @Override
  public void run() {
    for (ExecutorService threadPool : threadPools) {
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
}
