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

package io.airbyte.workers.temporal;

import com.google.common.base.Stopwatch;
import io.airbyte.workers.WorkerException;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.ActivityCompletionException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface CancellationHandler {

  void heartbeat(Runnable callback) throws WorkerException;

  class TemporalCancellationHandler implements CancellationHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(TemporalCancellationHandler.class);
    private static final Duration INTERVAL = Duration.ofSeconds(5);
    final ActivityExecutionContext context;
    final Stopwatch stopwatch;

    public TemporalCancellationHandler() {
      context = Activity.getExecutionContext();
      stopwatch = Stopwatch.createStarted();
    }

    @Override
    public void heartbeat(Runnable callback) throws WorkerException {
      if (stopwatch.elapsed(TimeUnit.SECONDS) > TimeUnit.SECONDS.convert(INTERVAL)) {
        try {
          LOGGER.info("heartbeating...");
          context.heartbeat(null);
        } catch (ActivityCompletionException e) {
          LOGGER.info("running callback...");
          callback.run();
          throw new WorkerException("Sync cancelled", e);
        }
        stopwatch.reset();
        stopwatch.start();
      }
    }

  }

}
