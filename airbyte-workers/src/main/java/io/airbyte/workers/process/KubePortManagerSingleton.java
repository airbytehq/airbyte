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

package io.airbyte.workers.process;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.EnvConfigs;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.TimeUnit;

public class KubePortManagerSingleton {

  private static BlockingQueue<Integer> workerPorts = new LinkedBlockingDeque<>(new EnvConfigs().getTemporalWorkerPorts());

  public static Integer take() throws InterruptedException {
    return workerPorts.poll(10, TimeUnit.MINUTES);
  }

  public static boolean offer(Integer port) {
    if (!workerPorts.contains(port)) {
      workerPorts.add(port);
      return true;
    }
    return false;
  }

  public static int getNumAvailablePorts() {
    return workerPorts.size();
  }

  @VisibleForTesting
  protected static void setWorkerPorts(Set<Integer> ports) {
    workerPorts = new LinkedBlockingDeque<>(ports);
  }

}
