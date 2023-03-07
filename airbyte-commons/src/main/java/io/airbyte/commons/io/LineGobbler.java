/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.logging.MdcScope;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class LineGobbler implements VoidCallable {

  private final static Logger LOGGER = LoggerFactory.getLogger(LineGobbler.class);
  private final static String GENERIC = "generic";

  public static void gobble(final InputStream is, final Consumer<String> consumer) {
    gobble(is, consumer, GENERIC, MdcScope.DEFAULT_BUILDER);
  }

  public static void gobble(final String message, final Consumer<String> consumer) {
    final InputStream stringAsSteam = new ByteArrayInputStream(message.getBytes(StandardCharsets.UTF_8));
    gobble(stringAsSteam, consumer);
  }

  public static void gobble(final String message) {
    gobble(message, LOGGER::info);
  }

  /**
   * Used to emit a visual separator in the user-facing logs indicating a start of a meaningful
   * temporal activity
   *
   * @param message
   */
  public static void startSection(final String message) {
    gobble("\r\n----- START " + message + " -----\r\n\r\n");
  }

  /**
   * Used to emit a visual separator in the user-facing logs indicating a end of a meaningful temporal
   * activity
   *
   * @param message
   */
  public static void endSection(final String message) {
    gobble("\r\n----- END " + message + " -----\r\n\r\n");
  }

  public static void gobble(final InputStream is, final Consumer<String> consumer, final MdcScope.Builder mdcScopeBuilder) {
    gobble(is, consumer, GENERIC, mdcScopeBuilder);
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
    this(is, consumer, executor, mdc, GENERIC, MdcScope.DEFAULT_BUILDER);
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final MdcScope.Builder mdcScopeBuilder) {
    this(is, consumer, executor, mdc, GENERIC, mdcScopeBuilder);
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
      String line = is.readLine();
      while (line != null) {
        try (final var mdcScope = containerLogMdcBuilder.build()) {
          consumer.accept(line);
        }
        line = is.readLine();
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
