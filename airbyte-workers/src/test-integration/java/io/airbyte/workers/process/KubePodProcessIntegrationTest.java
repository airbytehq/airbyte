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
import io.airbyte.workers.WorkerUtils;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.util.Config;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.ServerSocket;
import java.net.UnknownHostException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.apache.commons.lang.RandomStringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// requires kube running locally to run. If using Minikube it requires MINIKUBE=true
public class KubePodProcessIntegrationTest {

  private static final boolean IS_MINIKUBE = Boolean.parseBoolean(Optional.ofNullable(System.getenv("IS_MINIKUBE")).orElse("false"));
  private List<Integer> openPorts;
  private int heartbeatPort;
  private String heartbeatUrl;
  private ApiClient officialClient;
  private KubernetesClient fabricClient;
  private KubeProcessFactory processFactory;

  private static WorkerHeartbeatServer server;

  @BeforeEach
  public void setup() throws Exception {
    openPorts = new ArrayList<>(getOpenPorts(5));
    KubePortManagerSingleton.setWorkerPorts(new HashSet<>(openPorts.subList(1, openPorts.size() - 1)));

    heartbeatPort = openPorts.get(0);
    heartbeatUrl = getHost() + ":" + heartbeatPort;

    officialClient = Config.defaultClient();
    fabricClient = new DefaultKubernetesClient();
    processFactory = new KubeProcessFactory("default", officialClient, fabricClient, heartbeatUrl, getHost());

    server = new WorkerHeartbeatServer(heartbeatPort);
    server.startBackground();
  }

  @AfterEach
  public void teardown() throws Exception {
    server.stop();
  }

  @Test
  public void testSuccessfulSpawning() throws Exception {
    // start a finite process
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess("echo hi; sleep 1; echo hi2");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @Test
  public void testSuccessfulSpawningWithQuotes() throws Exception {
    // start a finite process
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess("echo \"h\\\"i\"; sleep 1; echo hi2");
    var output = new String(process.getInputStream().readAllBytes());
    assertEquals("h\"i\nhi2\n", output);
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @Test
  public void testPipeInEntrypoint() throws Exception {
    // start a process that has a pipe in the entrypoint
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess("echo hi | cat");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @Test
  public void testExitCodeRetrieval() throws Exception {
    // start a process that requests
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess("exit 10");
    process.waitFor();

    // the pod should be dead with the correct error code
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertEquals(10, process.exitValue());
  }

  @Test
  public void testMissingEntrypoint() throws WorkerException, InterruptedException {
    // start a process with an entrypoint that doesn't exist
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess(null);
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertEquals(127, process.exitValue());
  }

  @Test
  public void testKillingWithoutHeartbeat() throws Exception {
    // start an infinite process
    var availablePortsBefore = KubePortManagerSingleton.getNumAvailablePorts();
    final Process process = getProcess("while true; do echo hi; sleep 1; done");

    // kill the heartbeat server
    server.stop();

    // waiting for process
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getNumAvailablePorts());
    assertNotEquals(0, process.exitValue());
  }

  private static String getRandomFile(int lines) {
    var sb = new StringBuilder();
    for (int i = 0; i < lines; i++) {
      sb.append(RandomStringUtils.randomAlphabetic(100));
      sb.append("\n");
    }
    return sb.toString();
  }

  private Process getProcess(String entrypoint) throws WorkerException {
    // these files aren't used for anything, it's just to check for exceptions when uploading
    var files = ImmutableMap.of(
        "file0", "fixed str",
        "file1", getRandomFile(1),
        "file2", getRandomFile(100),
        "file3", getRandomFile(1000));

    return processFactory.create(
        "some-id",
        0,
        Path.of("/tmp/job-root"),
        "busybox:latest",
        false,
        files,
        entrypoint, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
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
      return (IS_MINIKUBE ? Inet4Address.getLocalHost().getHostAddress() : "host.docker.internal");
    } catch (UnknownHostException e) {
      throw new RuntimeException(e);
    }
  };

}
