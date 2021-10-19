/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.concurrency.VoidCallable;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class LineGobbler implements VoidCallable {

  private final static Logger LOGGER = LoggerFactory.getLogger(LineGobbler.class);
  private final static String DEFAULT_CALLER = "generic";
  private final static String DEFAULT_PREFIX = "";

  @VisibleForTesting final static String SEPARATOR = " - ";

  /**
   * Create a {@LineGobbler} which will forward the logs of the input stream a consumer.
   *
   * @param is       - the input stream to be consume
   * @param consumer - the consumer which will process the
   */
  public static void gobble(final InputStream is, final Consumer<String> consumer) {
    gobble(is, consumer, DEFAULT_CALLER);
  }

  /**
   * Create a {@LineGobbler} which will forward the logs of the input stream a consumer.
   *
   * @param is       - the input stream to be consume
   * @param consumer - the consumer which will process the
   * @param caller   - A caller, which is a tag that will be used when logging that the operation is success or failure
   */
  public static void gobble(final InputStream is, final Consumer<String> consumer, final String caller) {
    gobble(is, consumer, caller, DEFAULT_PREFIX);
  }

  /**
   * Create a {@LineGobbler} which will forward the logs of the input stream a consumer.
   *
   * @param is       - the input stream to be consume
   * @param consumer - the consumer which will process the
   * @param caller   - A caller, which is a tag that will be used when logging that the operation is success or failure
   * @param prefix   - A prefix that will be added to every line coming from the input stream, it will be seperated from the line by " - "
   */
  public static void gobble(final InputStream is, final Consumer<String> consumer, final String caller, final String prefix) {
    final ExecutorService executor = Executors.newSingleThreadExecutor();
    final Map<String, String> mdc = MDC.getCopyOfContextMap();
    final var gobbler = new LineGobbler(is, consumer, executor, mdc, caller, prefix);
    executor.submit(gobbler);
  }

  private final BufferedReader is;
  private final Consumer<String> consumer;
  private final ExecutorService executor;
  private final Map<String, String> mdc;
  private final String caller;
  private final String prefix;

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc) {
    this(is, consumer, executor, mdc, DEFAULT_CALLER);
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final String caller) {
    this(is, consumer, executor, mdc, caller, DEFAULT_PREFIX);
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final String caller,
              final String prefix) {
    this.is = IOs.newBufferedReader(is);
    this.consumer = consumer;
    this.executor = executor;
    this.mdc = mdc;
    this.caller = caller;
    this.prefix = prefix;
  }

  @Override
  public void voidCall() {
    MDC.setContextMap(mdc);
    try {
      String line;
      while ((line = is.readLine()) != null) {
        if (prefix != DEFAULT_PREFIX) {
          consumer.accept(prefix + SEPARATOR + line);
        } else {
          consumer.accept(line);
        }

      }
    } catch (final IOException i) {
      LOGGER.warn("{} gobbler IOException: {}. Typically happens when cancelling a job.", caller, i.getMessage());
    } catch (final Exception e) {
      LOGGER.error("{} gobbler error when reading stream", caller, e);
    } finally {
      executor.shutdown();
    }
  }

}
