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

package io.dataline.workers;

import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkerUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerUtils.class);

  public static void closeProcess(Process process) {
    closeProcess(process, 1, TimeUnit.MINUTES);
  }

  public static void closeProcess(Process process, int duration, TimeUnit timeUnit) {
    if (process == null) {
      return;
    }
    try {
      process.destroy();
      process.waitFor(duration, timeUnit);
      if (process.isAlive()) {
        process.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when closing process.", e);
    }
  }

  public static void cancelProcess(Process process) {
    closeProcess(process, 10, TimeUnit.SECONDS);
  }

  /**
   * Translates a StandardSyncInput into a StandardTapConfig. StandardTapConfig is a subset of
   * StandardSyncInput.
   */
  public static StandardTapConfig syncToTapConfig(StandardSyncInput sync) {
    return new StandardTapConfig()
    .withSourceConnectionImplementation(sync.getSourceConnectionImplementation())
    .withStandardSync(sync.getStandardSync())
    .withState(sync.getState());
  }

  /**
   * Translates a StandardSyncInput into a StandardTargetConfig. StandardTargetConfig is a subset of
   * StandardSyncInput.
   */
  public static StandardTargetConfig syncToTargetConfig(StandardSyncInput sync) {
    return new StandardTargetConfig()
    .withDestinationConnectionImplementation(sync.getDestinationConnectionImplementation())
    .withStandardSync(sync.getStandardSync());
  }

}
