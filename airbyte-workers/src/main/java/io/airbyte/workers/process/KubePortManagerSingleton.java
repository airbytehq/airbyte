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
 * The singleton pattern clarifies that only one copy of this class is intended to exist per
 * scheduler deployment.
 */
public class KubePortManagerSingleton {
  private static final Logger LOGGER = LoggerFactory.getLogger(KubePortManagerSingleton.class);

  private static KubePortManagerSingleton instance;

  private final int MAX_PORTS_PER_WORKER = 4; // A sync has two workers. Each worker requires 2 ports.
  private BlockingQueue<Integer> workerPorts;

  private KubePortManagerSingleton() {
    this(new EnvConfigs().getTemporalWorkerPorts());
  }
  private KubePortManagerSingleton(Set<Integer> ports) {
    workerPorts = new LinkedBlockingDeque<>(ports);
  }

  /**
   * Configures the instance by using the configuration available through
   * EnvConfigs; this must exist as env vars at runtime to be found, or
   * an empty set of ports will be used instead.
   * @return
   */
  public static synchronized KubePortManagerSingleton getInstance() {
    if (instance == null) {
      instance = new KubePortManagerSingleton();
    }
    return instance;
  }

  @VisibleForTesting
  /**
   * Configures the instance using the given set of ports; this is presumed to be used only
   * in a testing context and never reused after that in the same jvm.
   */
  protected synchronized static KubePortManagerSingleton getInstance(Set<Integer> ports) {
    if (instance == null) {
      instance = new KubePortManagerSingleton(ports);
    }
    return instance;
  }

  public Integer take() throws InterruptedException {
    return workerPorts.poll(10, TimeUnit.MINUTES);
  }

  public void offer(Integer port) {
    if (!workerPorts.contains(port)) {
      workerPorts.add(port);
    }
  }

  public int getNumAvailablePorts() {
    return workerPorts.size();
  }

  public int getSupportedWorkers() {
    return workerPorts.size() / MAX_PORTS_PER_WORKER;
  }

}
