/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class CloseableResourceManagerTest {

  @Test
  public void testHappyPath() {
    final CloseableResourceManager instance = CloseableResourceManager.getInstance();
    Assertions.assertNotNull(instance);

    final AtomicBoolean closed = new AtomicBoolean(false);
    instance.addCloseable(() -> closed.set(true));

    instance.closeAll();
    Assertions.assertTrue(closed.get());
  }

  @Test()
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

    Assertions.assertFalse(closed.get());
    Assertions.assertTrue(thrown);
  }

}
