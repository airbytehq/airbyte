package io.airbyte.integrations.util;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.RejectedExecutionHandler;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Create a ThreadPoolExecutor for execution of background tasks, etc.
 *
 * Opinionaed in the use of a blocking RejectedExecutionHandler in the event of
 * a full task list. Recommend you dont set the task list too high. If your process
 * is not making progress, we shouldn't require a very large task queue.
 *
 * Clean up and close the Executor by calling CloseableResourceManager.closeAll()
 * when done.
 */
public class ExecutorFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExecutorFactory.class);

  public static ThreadPoolExecutor getExecutor(final int maxThreads, final int maxWorkQueueSize) {
    final BlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<>(maxWorkQueueSize);

    final ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(1, maxThreads, 0, TimeUnit.MILLISECONDS, workQueue, new BlockingCallerPolicy());

    // track this resource so we can shut it down at the end of processing
    CloseableResourceManager.getInstance().addCloseable(() -> {
      threadPoolExecutor.shutdown();
      try {
        if (!threadPoolExecutor.awaitTermination(60, TimeUnit.SECONDS)) {
          LOGGER.error("Failed to await termination of executor");
          threadPoolExecutor.shutdownNow();
        }
      } catch (InterruptedException ex) {
        threadPoolExecutor.shutdownNow();
        Thread.currentThread().interrupt();
      }
    });
    return threadPoolExecutor;
  }

  /**
   * A RejectedExecutionHandler that will block until there is room in the queue to add a new Runnable.
   */
  static class BlockingCallerPolicy implements RejectedExecutionHandler {

    @Override
    public void rejectedExecution(final Runnable r, final ThreadPoolExecutor executor) {
      // Without this check the call hangs forever on the queue put.
      if (executor.isShutdown()) {
        throw new RejectedExecutionException("Executor is shutdown");
      }
      try {
        // block until there's room
        executor.getQueue().put(r);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new RejectedExecutionException("Unexpected InterruptedException", e);
      }
    }
  }
}
