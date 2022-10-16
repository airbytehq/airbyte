/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.functional.CheckedConsumer;
import java.util.concurrent.Callable;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;

class LifecycledCallableTest {

  private Callable<Integer> callable;
  private VoidCallable onStart;
  private CheckedConsumer<Exception, Exception> onException;
  private CheckedConsumer<Integer, Exception> onSuccess;
  private VoidCallable onFinish;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    callable = mock(Callable.class);
    onStart = mock(VoidCallable.class);
    onException = mock(CheckedConsumer.class);
    onSuccess = mock(CheckedConsumer.class);
    onFinish = mock(VoidCallable.class);
  }

  @Test
  void testSuccess() throws Exception {
    final LifecycledCallable<Integer> lc = new LifecycledCallable.Builder<>(callable)
        .setOnStart(onStart)
        .setOnException(onException)
        .setOnSuccess(onSuccess)
        .setOnFinish(onFinish)
        .build();

    when(callable.call()).thenReturn(1);

    assertEquals(1, lc.call());

    final InOrder inOrder = inOrder(callable, onStart, onException, onSuccess, onFinish);
    inOrder.verify(onStart).call();
    inOrder.verify(callable).call();
    inOrder.verify(onSuccess).accept(1);
    inOrder.verify(onFinish).call();
  }

  @Test
  void testException() throws Exception {
    final LifecycledCallable<Integer> lc = new LifecycledCallable.Builder<>(callable)
        .setOnStart(onStart)
        .setOnException(onException)
        .setOnSuccess(onSuccess)
        .setOnFinish(onFinish)
        .build();

    final RuntimeException re = new RuntimeException();
    when(callable.call()).thenThrow(re);

    assertThrows(RuntimeException.class, lc::call);

    final InOrder inOrder = inOrder(callable, onStart, onException, onSuccess, onFinish);
    inOrder.verify(onStart).call();
    inOrder.verify(callable).call();
    inOrder.verify(onException).accept(re);
    inOrder.verify(onFinish).call();
  }

}
