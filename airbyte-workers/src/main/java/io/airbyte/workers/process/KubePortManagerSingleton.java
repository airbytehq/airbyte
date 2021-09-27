/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

  public static void offer(Integer port) {
    if (!workerPorts.contains(port)) {
      workerPorts.add(port);
    }
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
