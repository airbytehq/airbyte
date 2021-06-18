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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.workers.WorkerException;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.UnknownHostException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// requires kube running locally to run. If using Minikube it requires MINIKUBE=true
public class KubePodProcessIntegrationTest {

  private static final boolean IS_MINIKUBE = Boolean.parseBoolean(Optional.ofNullable(System.getenv("IS_MINIKUBE")).orElse("false"));
  private static final List<Integer> OPEN_PORTS = new ArrayList<>(getOpenPorts(5));
  private static final List<Integer> OPEN_WORKER_PORTS = OPEN_PORTS.subList(1, OPEN_PORTS.size() - 1);
  private static final int HEARTBEAT_PORT = OPEN_PORTS.get(0);
  private static final String HEARTBEAT_URL = getHost() + ":" + HEARTBEAT_PORT;

  private final KubernetesClient kubeClient = new DefaultKubernetesClient();
  private final BlockingQueue<Integer> workerPorts = new LinkedBlockingDeque<>(OPEN_WORKER_PORTS);
  private final KubeProcessFactory processFactory = new KubeProcessFactory("default", kubeClient, HEARTBEAT_URL, workerPorts);

  private static WorkerHeartbeatServer server;

  @BeforeEach
  public void setup() throws Exception {
    server = new WorkerHeartbeatServer(HEARTBEAT_PORT);
    server.startBackground();
  }

  @AfterEach
  public void teardown() throws Exception {
    server.stop();
  }

  @Test
  public void testSuccessfulSpawning() throws Exception {
    // start a finite process
    final Process process = getProcess("echo hi; sleep 1; echo hi2");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(0, process.exitValue());
  }

  @Test
  public void testPipeInEntrypoint() throws Exception {
    // start a process that has a pipe in the entrypoint
    final Process process = getProcess("echo hi | cat");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(0, process.exitValue());
  }

  @Test
  public void testExitCodeRetrieval() throws Exception {
    // start a process that requests
    final Process process = getProcess("exit 10");
    process.waitFor();

    // the pod should be dead with the correct error code
    assertFalse(process.isAlive());
    assertEquals(10, process.exitValue());
  }

  @Test
  public void testMissingEntrypoint() throws WorkerException, InterruptedException {
    // start a process with an entrypoint that doesn't exist
    final Process process = getProcess("ksaiiiasdfjklaslkei");
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertEquals(127, process.exitValue());
  }

  @Test
  public void testKillingWithoutHeartbeat() throws Exception {
    // start an infinite process
    final Process process = getProcess("while true; do echo hi; sleep 1; done");

    // kill the heartbeat server
    server.stop();

    // waiting for process
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertNotEquals(0, process.exitValue());
  }

  private Process getProcess(String entrypoint) throws WorkerException {
    return processFactory.create(
        "some-id",
        0,
        Path.of("/tmp/job-root"),
        "busybox:latest",
        false,
        ImmutableMap.of(),
        entrypoint);
  }

  private static Set<Integer> getOpenPorts(int count) {
    final Set<ServerSocket> servers = new HashSet<>();
    final Set<Integer> ports = new HashSet<>();

    try {
      for (int i = 0; i < count; i++) {
        var server = new ServerSocket(0);
        servers.add(server);
        ports.add(server.getLocalPort());
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    } finally {
      for (ServerSocket server : servers) {
        Exceptions.swallow(server::close);
      }
    }

    return ports;
  }

  private static String getHost() {
    try {
      return (IS_MINIKUBE ? InetAddress.getLocalHost().getHostAddress() : "host.docker.internal");
    } catch (UnknownHostException e) {
      throw new RuntimeException(e);
    }
  };

}
