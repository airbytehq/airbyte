/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.commons.io;

import io.dataline.commons.concurrency.VoidCallable;
import java.io.BufferedReader;
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
