package io.airbyte.integrations.async;

import io.airbyte.integrations.util.CloseableResourceManager;
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
 * a full task list. Recommend you don't set the task list too high. If your process
 * is not making progress, we shouldn't require a very large task queue.
 *
 * Clean up and close the Executor by calling CloseableResourceManager.closeAll()
 * when done.
 */
public class ExecutorFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExecutorFactory.class);
  public static final int CORE_THREAD_POOL_SIZE = 1;
  public static final int KEEP_ALIVE_TIME_MILLIS = 0;
  public static final int DEFAULT_AWAIT_TERMINATION_SECONDS = 60;
  public static final int MAXIMUM_THREAD_POOL_SIZE = 1;

  public static ThreadPoolExecutor getExecutor(final int maxWorkQueueSize) {
    final BlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<>(maxWorkQueueSize);

    final ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(CORE_THREAD_POOL_SIZE, MAXIMUM_THREAD_POOL_SIZE, KEEP_ALIVE_TIME_MILLIS, TimeUnit.MILLISECONDS, workQueue, new BlockingCallerPolicy());

    // track this resource so we can shut it down at the end of processing
    CloseableResourceManager.getInstance().addCloseable(() -> shutdown(threadPoolExecutor));
    return threadPoolExecutor;
  }

   static void shutdown(final ThreadPoolExecutor threadPoolExecutor) {
    shutdown(threadPoolExecutor, DEFAULT_AWAIT_TERMINATION_SECONDS);
   }

   static void shutdown(final ThreadPoolExecutor threadPoolExecutor, final int awaitTerminationSeconds) {
    threadPoolExecutor.shutdown();
    try {
      if (!threadPoolExecutor.awaitTermination(awaitTerminationSeconds, TimeUnit.SECONDS)) {
        LOGGER.error("Failed to await termination of executor");
        threadPoolExecutor.shutdownNow();
      }
    } catch (InterruptedException ex) {
      threadPoolExecutor.shutdownNow();
      Thread.currentThread().interrupt();
    }
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
