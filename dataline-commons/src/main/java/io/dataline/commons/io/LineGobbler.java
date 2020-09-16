package io.dataline.commons.io;

import io.dataline.commons.concurrency.VoidCallable;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LineGobbler implements VoidCallable {

  private final static Logger LOGGER = LoggerFactory.getLogger(LineGobbler.class);

  public static void gobble(final InputStream is, final Consumer<String> consumer) {
   final ExecutorService executor = Executors.newSingleThreadExecutor();
    executor.submit(new LineGobbler(is, consumer, executor));
  }

  private final BufferedReader is;
  private final Consumer<String> consumer;
  private final ExecutorService executor;

  LineGobbler(final InputStream is, final Consumer<String> consumer, final ExecutorService executor) {
    this.is = IOs.newBufferedReader(is);
    this.consumer = consumer;
    this.executor = executor;
  }

  @Override
  public void voidCall() {
    String line;
    try {
      while ((line = is.readLine()) != null) {
        consumer.accept(line);
      }
    } catch (Exception e) {
      LOGGER.error("Error when reading stream", e);
    } finally {
      executor.shutdown();
    }
  }
}
