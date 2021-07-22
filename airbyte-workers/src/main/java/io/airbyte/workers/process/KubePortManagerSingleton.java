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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Convenience wrapper around a thread-safe BlockingQueue. Keeps track of available ports for Kube
 * Pod Processes.
 *
 * Although this data structure can do without the wrapper class, this class allows easier testing
 * via the {@link #getNumAvailablePorts()} function.
 *
 * The singleton pattern clarifies that only one copy of this class is intended to exists per
 * scheduler deployment.
 */
public class KubePortManagerSingleton {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubePortManagerSingleton.class);
  private static final int MAX_PORTS_PER_WORKER = 4; // A sync has two workers. Each worker requires 2 ports.
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

  public static int getSupportedWorkers() {
    return workerPorts.size() / MAX_PORTS_PER_WORKER;
  }

  @VisibleForTesting
  protected static void setWorkerPorts(Set<Integer> ports) {
    workerPorts = new LinkedBlockingDeque<>(ports);
  }

}
