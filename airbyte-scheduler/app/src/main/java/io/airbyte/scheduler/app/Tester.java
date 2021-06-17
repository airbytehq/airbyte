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

package io.airbyte.scheduler.app;

import com.google.common.collect.ImmutableMap;
import io.airbyte.scheduler.app.kube.WorkerHeartbeatServer;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;

public class Tester {

  public static void main(String[] args) throws Exception {
    System.out.println("testing...");

    WorkerHeartbeatServer server = new WorkerHeartbeatServer(4000);
    server.startBackground();

    final KubernetesClient kubeClient = new DefaultKubernetesClient();
    final BlockingQueue<Integer> workerPorts = new LinkedBlockingDeque<>(List.of(4001, 4002, 4003));
    KubeProcessFactory processFactory = new KubeProcessFactory("default", kubeClient, "host.docker.internal:4000", workerPorts);

    Process process = processFactory.create(
        "some-id",
        0,
        Path.of("/tmp/job-root"),
        "airbyte/source-exchange-rates:0.2.3",
        false,
        ImmutableMap.of(),
        "while true; do echo hi; sleep 1; done");
    System.out.println("sleeping...");
    Thread.sleep(5000);

    System.out.println("shutting down server...");
    server.stop();

    System.out.println("waiting for process...");
    process.waitFor();

    // Process process = processFactory.create(
    // "some-id",
    // 0,
    // Path.of("/tmp/job-root"),
    // "airbyte/source-exchange-rates:0.2.3",
    // false,
    // ImmutableMap.of(),
    // "python /airbyte/integration_code/main.py",
    // "spec");
    //
    // System.out.println("waiting for process...");
    // process.waitFor();
    //
    // System.out.println("shutting down server...");
    // server.stop();

    System.out.println("done!");
  }

}
