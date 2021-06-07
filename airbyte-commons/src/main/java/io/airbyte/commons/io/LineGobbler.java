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

  public static void gobble(final InputStream is, final Consumer<String> consumer) {
    gobble(is, consumer, "generic");
  }

  public static void gobble(final InputStream is, final Consumer<String> consumer, String caller) {
    final ExecutorService executor = Executors.newSingleThreadExecutor();
    final Map<String, String> mdc = MDC.getCopyOfContextMap();
    var gobbler = new LineGobbler(is, consumer, executor, mdc, caller);
    executor.submit(gobbler);
  }

  private final BufferedReader is;
  private final Consumer<String> consumer;
  private final ExecutorService executor;
  private final Map<String, String> mdc;
  private final String caller;

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc) {
    this(is, consumer, executor, mdc, "generic");
  }

  LineGobbler(final InputStream is,
              final Consumer<String> consumer,
              final ExecutorService executor,
              final Map<String, String> mdc,
              final String caller) {
    this.is = IOs.newBufferedReader(is);
    this.consumer = consumer;
    this.executor = executor;
    this.mdc = mdc;
    this.caller = caller;
  }

  @Override
  public void voidCall() {
    MDC.setContextMap(mdc);
    try {
      String line;
      while ((line = is.readLine()) != null) {
        consumer.accept(line);
      }
    } catch (IOException i) {
      LOGGER.warn("{} gobbler IOException: {}. Typically happens when cancelling a job.", caller, i.getMessage());
    } catch (Exception e) {
      LOGGER.error("{} gobbler error when reading stream", caller, e);
    } finally {
      executor.shutdown();
    }
  }

}
