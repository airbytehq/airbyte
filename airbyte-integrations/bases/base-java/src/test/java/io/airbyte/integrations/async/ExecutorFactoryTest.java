/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.atomic.AtomicBoolean;
import org.hamcrest.MatcherAssert;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ExecutorFactoryTest {

  public static final int ONE_SECOND = 1;

  /**
   * Happy path tests for creation of the executor and its basic properties
   */
  @Test
  public void testCreateExecutor() {
    final ThreadPoolExecutor executor = ExecutorFactory.getExecutor(1);
    Assertions.assertNotNull(executor);
    assertEquals(executor.getCorePoolSize(), 1);
    assertEquals(executor.getMaximumPoolSize(), 1);
    assertEquals(executor.getQueue().remainingCapacity(), 1);
  }

  /**
   * Test that the Blocking RejectedExecutionHandler we use blocks after the specified numbers of items
   * is waiting in the queue
   */
  @Test
  public void testRejectedExecution() {
    // single thread, single task queue slot
    final ThreadPoolExecutor executor = ExecutorFactory.getExecutor(1);

    // submit a task that will take >1s to complete
    executor.submit(() -> {
      try {
        Thread.sleep(1500);
      } catch (InterruptedException e) {
        // do nothing
      }
    });
    // submit a second task that should be enqueued and waiting
    executor.submit(() -> {
      try {
        Thread.sleep(100);
      } catch (InterruptedException e) {
        // do nothing
      }
    });
    // is there one item in the queue?
    assertEquals(executor.getQueue().size(), 1);

    // start the timer and attempt to add another task, we expect this to block awaiting space in the queue
    long submitStartTime = System.currentTimeMillis();
    executor.submit(() -> {
      try {
        Thread.sleep(1);
      } catch (InterruptedException e) {
        // do nothing
      }
    });
    long submitStopTime = System.currentTimeMillis();

    // verify that we waited at least 1s (based on the thread sleeps above
    final long totalWaitTime = submitStopTime - submitStartTime;
    MatcherAssert.assertThat(totalWaitTime, Matchers.greaterThan(1000L));
    MatcherAssert.assertThat(totalWaitTime, Matchers.lessThan(2000L));
  }

  /**
   * Test a normal shutdown with a short running task
   */
  @Test
  public void testNormalShutdown() throws ExecutionException, InterruptedException {
    final ThreadPoolExecutor executor = ExecutorFactory.getExecutor(1);

    // submit a callable that sleep for 1 s and then returns
    final Future<String> future = executor.submit(() -> {
      Thread.sleep(1000);
      return "done";
    });

    // shut down the executor, start a timer
    final long startShutdownTime = System.currentTimeMillis();
    ExecutorFactory.shutdown(executor);

    final long stopShutdownTime = System.currentTimeMillis();
    final long totalShutdownTime = stopShutdownTime - startShutdownTime;

    // should be close to this but we cant guarantee a time across all envs.
    MatcherAssert.assertThat(totalShutdownTime, Matchers.greaterThan(800L));
    MatcherAssert.assertThat(totalShutdownTime, Matchers.lessThan(1500L));

    // the task should have completed
    assertTrue(future.isDone());
    assertFalse(future.isCancelled());

    // is the return value as expected? just a sanity check
    assertEquals("done", future.get());
  }

  /**
   * Submit a "long running" task and then shutdown with a "short" waiting time. We expect in that case
   * that the task will be "interrupted" and not complete normally.
   */
  @Test
  public void testShutdownWithLongTask() {
    final ThreadPoolExecutor executor = ExecutorFactory.getExecutor(1);

    // submit a callable that sleep for 5s and then returns
    final Future<String> future = executor.submit(() -> {
      Thread.sleep(5000);
      return "done";
    });

    // shut down the executor with a wait time of 1s and start a timer
    final long startShutdownTime = System.currentTimeMillis();
    ExecutorFactory.shutdown(executor, ONE_SECOND);

    // the task should not have completed
    assertFalse(future.isCancelled()); // tasks dont get cancelled, per se, they get interrupted
    assertFalse(future.isDone());

    // we expect that this task was interrupted after the specified wait time
    boolean interrupted = false;
    try {
      future.get();
    } catch (Exception e) {
      interrupted = true;
      assertTrue(e.getCause() instanceof InterruptedException);
    }
    assertTrue(interrupted);

    // verify that the time waiting was around the time we specified for timeout
    final long stopShutdownTime = System.currentTimeMillis();
    final long totalShutdownTime = stopShutdownTime - startShutdownTime;
    MatcherAssert.assertThat(totalShutdownTime, Matchers.greaterThan(800L));
    MatcherAssert.assertThat(totalShutdownTime, Matchers.lessThan(1500L));
  }

  /**
   * Adding a Callable after shutdown should reject the addition with a RejectedExecutionException
   */
  @Test
  public void testAddJobAfterShutdown() {
    final ThreadPoolExecutor executor = ExecutorFactory.getExecutor(1);
    assertNotNull(executor);

    // we should accept no new Callables after this
    ExecutorFactory.shutdown(executor);

    boolean thrown = false;
    final AtomicBoolean taskRun = new AtomicBoolean(false);
    // now try to add a task, we expect an exception
    try {
      executor.submit(() -> {
        // should not run or be accepted by the resource manager
        taskRun.set(true);
      });
    } catch (RejectedExecutionException ree) {
      thrown = true;
    }

    // we expect the specific exception to have been thrown and the task to have not run
    assertTrue(thrown);
    assertFalse(taskRun.get());
  }

}
