/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class CloseableResourceManagerTest {

  /**
   * Basic test that a Closeable added to the resource manager is actually closed on closeAll
   */
  @Test
  public void testHappyPath() {
    final CloseableResourceManager instance = CloseableResourceManager.getInstance();
    Assertions.assertNotNull(instance);
    Assertions.assertSame(instance, CloseableResourceManager.getInstance());

    // we use an AtomicBoolean because it can be final here and still settable within the anonymous class
    final AtomicBoolean closed = new AtomicBoolean(false);
    instance.addCloseable(() -> closed.set(true));

    // close... did it actually close?
    instance.closeAll();
    Assertions.assertTrue(closed.get());
  }

  /**
   * Get an instance of the resource manager and then call closeAll. Are we prevented from adding new objects?
   */
  @Test
  public void testRejectedExecution() {
    final CloseableResourceManager instance = CloseableResourceManager.getInstance();
    Assertions.assertNotNull(instance);

    final AtomicBoolean closed = new AtomicBoolean(false);
    boolean thrown = false;
    instance.closeAll();
    try {
      instance.addCloseable(() -> closed.set(true));
    } catch (RejectedExecutionException ree) {
      thrown = true;
    }

    // expect the new task to have not been added and instead have closed
    Assertions.assertFalse(closed.get());
    Assertions.assertTrue(thrown);
  }

}
