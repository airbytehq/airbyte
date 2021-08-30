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

package io.airbyte.worker;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.worker.process.DockerProcessFactory;
import io.airbyte.worker.process.KubeProcessFactory;
import io.airbyte.worker.process.ProcessFactory;
import io.airbyte.worker.temporal.TemporalPool;
import io.airbyte.worker.temporal.TemporalUtils;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.util.Config;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class WorkerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerApp.class);
  public static final int KUBE_HEARTBEAT_PORT = 9000;

  private final Path workspaceRoot;
  private final ProcessFactory processFactory;
  private final WorkflowServiceStubs temporalService;

  public WorkerApp(Path workspaceRoot,
                   ProcessFactory processFactory,
                   WorkflowServiceStubs temporalService) {
    this.workspaceRoot = workspaceRoot;
    this.processFactory = processFactory;
    this.temporalService = temporalService;
  }

  public void start() {
    final TemporalPool temporalPool = new TemporalPool(temporalService, workspaceRoot, processFactory);
    temporalPool.run();
  }

  private static ProcessFactory getProcessBuilderFactory(Configs configs) throws IOException {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final ApiClient officialClient = Config.defaultClient();
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getKubeNamespace());
      return new KubeProcessFactory(configs.getKubeNamespace(), officialClient, fabricClient, kubeHeartbeatUrl);
    } else {
      return new DockerProcessFactory(
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork());
    }
  }

  public static void main(String[] args) throws IOException {
    final Configs configs = new EnvConfigs();

    // todo: add proper wait for server

    // todo: move to a non-scheduler log endpoint for workers, can be a larger issue
    MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, LogClientSingleton.getSchedulerLogsRoot(configs).toString());

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    final String temporalHost = configs.getTemporalHost();
    LOGGER.info("temporalHost = " + temporalHost);

    final ProcessFactory processFactory = getProcessBuilderFactory(configs);

    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(temporalHost);

    new WorkerApp(workspaceRoot, processFactory, temporalService).start();
  }

}
