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

package io.airbyte.integrations.base;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class FailureTrackingConsumer<T> implements DestinationConsumer<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(FailureTrackingConsumer.class);

  private boolean hasFailed = false;

  protected abstract void acceptTracked(T t) throws Exception;

  public void accept(T t) throws Exception {
    try {
      acceptTracked(t);
    } catch (Exception e) {
      hasFailed = true;
      throw e;
    }
  }

  protected abstract void close(boolean hasFailed) throws Exception;

  public void close() throws Exception {
    LOGGER.info("hasFailed: {}.", hasFailed);
    close(hasFailed);
  }

}
