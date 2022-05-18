/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import java.io.InputStream;
import org.junit.jupiter.api.Test;

public class CloseableShutdownHookTest {

  @Test
  void testRegisteringShutdownHook() throws Exception {
    final InputStream closeable = mock(InputStream.class);
    final CloseableQueue autoCloseable = mock(CloseableQueue.class);
    final String notCloseable = "Not closeable";

    final Thread thread = CloseableShutdownHook.buildShutdownHookThread(closeable, autoCloseable, notCloseable, null);
    thread.run();

    verify(closeable, times(1)).close();
    verify(autoCloseable, times(1)).close();
  }

}
