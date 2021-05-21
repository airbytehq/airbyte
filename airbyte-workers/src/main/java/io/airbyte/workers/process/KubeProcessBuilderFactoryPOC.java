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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodList;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactoryPOC {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactoryPOC.class);

  private static final KubernetesClient KUBE_CLIENT = new DefaultKubernetesClient();
  private static final int PORT = 9001;

  // todo: this should really be cached
  private static String getCommandFromImage(String imageName) throws IOException {
    final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

    final String podName = "airbyte-command-fetcher-" + suffix;

    final List<String> cmd =
        Lists.newArrayList(
            "kubectl",
            "run",
            "--generator=run-pod/v1",
            "--rm",
            "-i",
            "--pod-running-timeout=24h",
            "--image=" + imageName,
            "--command=true",
            "--restart=Never",
            podName,
            "--",
            "sh",
            "-c",
            "echo \"AIRBYTE_ENTRYPOINT=$AIRBYTE_ENTRYPOINT\"");

    Process start = new ProcessBuilder(cmd).start();

    try (BufferedReader reader = IOs.newBufferedReader(start.getInputStream())) {
      String line;
      while ((line = reader.readLine()) != null && !line.contains("AIRBYTE_ENTRYPOINT"));

      if (line == null || !line.contains("AIRBYTE_ENTRYPOINT")) {
        throw new RuntimeException("Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
      } else {
        String[] splits = line.split("=", 2);
        if (splits.length == 1) {
          throw new RuntimeException(
              "Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
        } else {
          return splits[1];
        }
      }
    }
  }

  private static void createPodAndWaitTillReady(String imageId) {}

  private static void saveJaredWork() {
    try {
      // todo: test this with args that are used by the process
      Process process = new KubeProcessBuilderFactory(Path.of("stdout_template.yaml"))
          .create(0L, 0, Path.of("/tmp"), "np_source:dev", null)
          .start();

      process.getOutputStream().write(100);
      process.getInputStream().read();

      // after running this main:
      // kubectl port-forward airbyte-worker-0-0-fmave 9000:9000
      // socat -d -d -d TCP-LISTEN:9000,bind=127.0.0.1 stdout

      LOGGER.info("waiting...");
      int code = process.waitFor();
      LOGGER.info("code = " + code);
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
      e.printStackTrace();
    }
  }

  private static String getPodIP(String podName) {
    // TODO: Why does directly searching for the pod not work?
    // LOGGER.info(destPod.getStatus().getPodIP());
    // destPod = client.resource(destPod).get();
    // LOGGER.info("Status: {}", destPod.getStatus());
    // LOGGER.info("IP: {}", destPod.getStatus().getPodIP());
    // IP = destPod.getStatus().getPodIP();

    // TODO: We could assign labels to pods to narrow the search.
    PodList pods = KUBE_CLIENT.pods().inNamespace("default").list();
    for (Pod p : pods.getItems()) {
      // Filter by pod and retrieve IP.
      if (p.getMetadata().getName().equals(podName)) {
        LOGGER.info("Found IP!");
        return p.getStatus().getPodIP();
      }
    }

    return null;
  }

  // TODO: It might be easier to do this using the same Socat pattern we use in the
  //  Dockerfile and be reading from a file.
  private static void startListeningOnPort(int port) {
    Executors.newSingleThreadExecutor().submit(() -> {
      try (var serverSocket = new ServerSocket(port)) {
        LOGGER.info("Created server and waiting for connection..");
        var socket = serverSocket.accept();
        LOGGER.info("Accepted connection!");
        var input = socket.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(input));
//        while(!reader.ready())
        while (true) {
          final var line = reader.readLine();
          if (line == null) break;

          LOGGER.info("Destination sent: {}", line);
        }
      } catch (IOException e) {
        LOGGER.error("Error starting socket reader: ",e);
      }
    });
  }

  private static void createIfNotExisting(String podName, Pod def) throws InterruptedException {
    LOGGER.info("Checking pod: {}", podName);
    var podSet = KUBE_CLIENT.pods().inNamespace("default").list().getItems().stream()
        .filter(pod -> pod.getMetadata().getName().equals(podName)).collect(Collectors.toSet());
    if (podSet.size() == 0) {
      LOGGER.info("Pod {} does not exist", podName);
      Pod destPod = KUBE_CLIENT.pods().create(def);
      LOGGER.info("Created pod: {}, waiting for it to be ready", destPod.getMetadata().getName());
      KUBE_CLIENT.resource(destPod).waitUntilReady(1, TimeUnit.MINUTES);
      LOGGER.info("Pod {} ready", podName);
    }
  }

  private static void runSampleKubeWorker() throws InterruptedException, IOException {
    String myIp = InetAddress.getLocalHost().getHostAddress();
    LOGGER.info("Kube sync worker ip: {}", myIp);

    var destPodName = "kube-destination-sample";

    // Load spec and swap in worker ip.
    var template = MoreResources.readResource("kube_queue_poc/kube-destination-sample-pod.yaml");
    var rendered = template.replaceAll("WORKER_IP", myIp);
    var renderedStream = new ByteArrayInputStream(rendered.getBytes());
    var destPodDef = KUBE_CLIENT.pods().load(renderedStream).get();
    LOGGER.info("Loaded spec");

    // TODO: 1) The container image needs to line up with the actual spec. 2) Why isn't this working?
//    var containers = destPodDef.getSpec().getContainers();
//    System.out.println(containers.get(0));
//    getCommandFromImage(containers.get(0).getImage());

    // Start a listening server for the Destination to connect to.
    startListeningOnPort(9001);

    createIfNotExisting(destPodName, destPodDef);
    String destPodIp = getPodIP(destPodName);
    LOGGER.info("Dest pod ip: {}", destPodIp);

    // Send something!
    var socketToDestStdIo = new Socket(destPodIp, PORT);
    var toDest = new PrintWriter(socketToDestStdIo.getOutputStream(), true);
    toDest.println("Hello!");
    toDest.println("a!");
    toDest.println("b!");
    toDest.println("c!");
    toDest.println("d!");
    toDest.close();

    KUBE_CLIENT.pods().delete(destPodDef);
    // TODO: Why does this wait not work?
    KUBE_CLIENT.resource(destPodDef).waitUntilCondition(pod -> !pod.getStatus().getPhase().equals("Terminating"), 1, TimeUnit.MINUTES);
    KUBE_CLIENT.close();
  }

  public static void main(String[] args) throws InterruptedException, IOException {
    runSampleKubeWorker();
  }

}
