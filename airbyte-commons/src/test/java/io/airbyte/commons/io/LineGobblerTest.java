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

package io.airbyte.commons.io;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.google.common.collect.ImmutableMap;
import com.google.common.util.concurrent.MoreExecutors;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class LineGobblerTest {

  @Test
  @SuppressWarnings("unchecked")
  void readAllLines() {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    final InputStream is = new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8));
    final ExecutorService executor = spy(MoreExecutors.newDirectExecutorService());

    executor.submit(new LineGobbler(is, consumer, executor, ImmutableMap.of()));

    Mockito.verify(consumer).accept("test");
    Mockito.verify(consumer).accept("test2");
    Mockito.verify(executor).shutdown();
  }

  @Test
  @SuppressWarnings("unchecked")
  void shutdownOnSuccess() {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    final InputStream is = new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8));
    final ExecutorService executor = spy(MoreExecutors.newDirectExecutorService());

    executor.submit(new LineGobbler(is, consumer, executor, ImmutableMap.of()));

    Mockito.verify(consumer, Mockito.times(2)).accept(anyString());
    Mockito.verify(executor).shutdown();
  }

  @Test
  @SuppressWarnings("unchecked")
  void shutdownOnError() {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    Mockito.doThrow(RuntimeException.class).when(consumer).accept(anyString());
    final InputStream is = new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8));
    final ExecutorService executor = spy(MoreExecutors.newDirectExecutorService());

    executor.submit(new LineGobbler(is, consumer, executor, ImmutableMap.of()));

    verify(consumer).accept(anyString());
    Mockito.verify(executor).shutdown();
  }

}
