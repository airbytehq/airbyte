/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.logging.MdcScope;
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

  public static void gobble(final InputStream is, final Consumer<String> consumer) {
    gobble(is, consumer, "generic", MdcScope.DEFAULT_BUILDER);
  }

  public static void gobble(final InputStream is, final Consumer<String> consumer, final MdcScope.Builder mdcScopeBuilder) {
    gobble(is, consumer, "generic", mdcScopeBuilder);
  }

  public static void gobble(final InputStream is, final Consumer<String> consumer, final String caller, final MdcScope.Builder mdcScopeBuilder) {
    final ExecutorService executor = Executors.newSingleThreadExecutor();
    final Map<String, String> mdc = MDC.getCopyOfContextMap();
    final var gobbler = new LineGobbler(is, consumer, executor, mdc, caller, mdcScopeBuilder);
    executor.submit(gobbler);
  }

  private final BufferedReader is;
  private final Consumer<String> consumer;
  private final ExecutorService executor;
  private final Map<String, String> mdc;
  private final String caller;
  private final MdcScope.Builder containerLogMdcBuilder;

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc) {
    this(is, consumer, executor, mdc, "generic", MdcScope.DEFAULT_BUILDER);
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final MdcScope.Builder mdcScopeBuilder) {
    this(is, consumer, executor, mdc, "generic", mdcScopeBuilder);
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final String caller,
              final MdcScope.Builder mdcScopeBuilder) {
    this.is = IOs.newBufferedReader(is);
    this.consumer = consumer;
    this.executor = executor;
    this.mdc = mdc;
    this.caller = caller;
    this.containerLogMdcBuilder = mdcScopeBuilder;
  }

  @Override
  public void voidCall() {
    MDC.setContextMap(mdc);
    try {
      String line;
      while ((line = is.readLine()) != null) {
        try (final var mdcScope = containerLogMdcBuilder.build()) {
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
