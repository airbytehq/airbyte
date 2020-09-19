/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
    LifecycledCallable<Integer> lc = new LifecycledCallable.Builder<>(callable)
        .setOnStart(onStart)
        .setOnException(onException)
        .setOnSuccess(onSuccess)
        .setOnFinish(onFinish)
        .build();

    when(callable.call()).thenReturn(1);

    assertEquals(1, lc.call());

    InOrder inOrder = inOrder(callable, onStart, onException, onSuccess, onFinish);
    inOrder.verify(onStart).call();
    inOrder.verify(callable).call();
    inOrder.verify(onSuccess).accept(1);
    inOrder.verify(onFinish).call();
  }

  @Test
  void testException() throws Exception {
    LifecycledCallable<Integer> lc = new LifecycledCallable.Builder<>(callable)
        .setOnStart(onStart)
        .setOnException(onException)
        .setOnSuccess(onSuccess)
        .setOnFinish(onFinish)
        .build();

    RuntimeException re = new RuntimeException();
    when(callable.call()).thenThrow(re);

    assertThrows(RuntimeException.class, lc::call);

    InOrder inOrder = inOrder(callable, onStart, onException, onSuccess, onFinish);
    inOrder.verify(onStart).call();
    inOrder.verify(callable).call();
    inOrder.verify(onException).accept(re);
    inOrder.verify(onFinish).call();
  }

}
