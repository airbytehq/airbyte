package io.dataline.commons.io;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentMatchers;
import org.mockito.Mockito;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.never;

class LineGobblerTest {

  @Test
  @SuppressWarnings("unchecked")
  void readAllLines() {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    final InputStream is = new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8));

    LineGobbler.gobble(is, consumer);

    Mockito.verify(consumer).accept("test");
    Mockito.verify(consumer).accept("test2");
  }

  @Test
  @SuppressWarnings("unchecked")
  void shutdownOnSuccess() throws InterruptedException {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    final InputStream is = new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8));

    final ExecutorService executor = Executors.newSingleThreadExecutor();
    executor.submit(new LineGobbler(is, consumer, executor));

    Mockito.verify(consumer, Mockito.times(2)).accept(anyString());
    executor.awaitTermination(10, TimeUnit.SECONDS);
    Assertions.assertTrue(executor.isTerminated());
  }

  @Test
  @SuppressWarnings("unchecked")
  void shutdownOnError() throws InterruptedException {
    final Consumer<String> consumer = Mockito.mock(Consumer.class);
    Mockito.doThrow(RuntimeException.class).when(consumer).accept(anyString());
    final InputStream is = Mockito.spy(new ByteArrayInputStream("test\ntest2\n".getBytes(StandardCharsets.UTF_8)));


    final ExecutorService executor = Executors.newSingleThreadExecutor();
    executor.submit(new LineGobbler(is, consumer, executor));

    Mockito.verify(consumer, never()).accept(anyString());
    executor.awaitTermination(10, TimeUnit.SECONDS);
    Assertions.assertTrue(executor.isTerminated());
  }
}
