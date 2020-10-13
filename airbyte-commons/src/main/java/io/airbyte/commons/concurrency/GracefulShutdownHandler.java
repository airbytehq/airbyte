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

import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GracefulShutdownHandler extends Thread {

  private static final Logger LOGGER = LoggerFactory.getLogger(GracefulShutdownHandler.class);
  private final Duration terminateWaitDuration;
  private final ExecutorService[] threadPools;

  public GracefulShutdownHandler(Duration terminateWaitDuration, final ExecutorService... threadPools) {
    this.terminateWaitDuration = terminateWaitDuration;
    this.threadPools = threadPools;
  }

  @Override
  public void run() {
    for (ExecutorService threadPool : threadPools) {
      threadPool.shutdown();

      try {
        if (!threadPool.awaitTermination(terminateWaitDuration.getSeconds(), TimeUnit.SECONDS)) {
          LOGGER.error("Unable to kill threads by shutdown timeout.");
        }
      } catch (InterruptedException e) {
        LOGGER.error("Wait for graceful thread shutdown interrupted.", e);
      }
    }
  }

}
