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

import com.google.common.base.Preconditions;
import io.fabric8.kubernetes.api.model.Container;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.output.NullOutputStream;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubePodProcess extends Process {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcess.class);

  private static final int STDIN_REMOTE_PORT = 9001;

  private final KubernetesClient client;
  private final Pod podDefinition;

  private final OutputStream stdin;
  private InputStream stdout;
  private final ServerSocket stdoutServerSocket;
  private final ExecutorService executorService;

  // TODO(Davin): Cache this result.
  public static String getCommandFromImage(KubernetesClient client, String imageName) throws IOException, InterruptedException {
    final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

    final String podName = "airbyte-command-fetcher-" + suffix;

    Container commandFetcher = new ContainerBuilder()
        .withName("airbyte-command-fetcher")
        .withImage(imageName)
        .withCommand("sh", "-c", "echo \"AIRBYTE_ENTRYPOINT=$AIRBYTE_ENTRYPOINT\"")
        .build();

    Pod pod = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName(podName)
        .endMetadata()
        .withNewSpec()
        .withRestartPolicy("Never")
        .withContainers(commandFetcher)
        .endSpec()
        .build();
    LOGGER.info("Creating pod...");
    Pod podDefinition = client.pods().inNamespace("default").createOrReplace(pod);
    LOGGER.info("Waiting until command fetcher pod completes...");
    client.resource(podDefinition).waitUntilCondition(p -> p.getStatus().getPhase().equals("Succeeded"), 20, TimeUnit.SECONDS);

    var logs = client.pods().inNamespace("default").withName(podName).getLog();
    if (!logs.contains("AIRBYTE_ENTRYPOINT")) {
      // this should not happen
      throw new RuntimeException("Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
    }

    var envVal = logs.split("=")[1].strip();
    if (envVal.isEmpty()) {
      throw new RuntimeException(
          "Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
    }
    return envVal;
  }

  public static String getPodIP(KubernetesClient client, String podName) {
    var pod = client.pods().inNamespace("default").withName(podName).get();
    if (pod == null) {
      throw new RuntimeException("Error: unable to find pod!");
    }
    return pod.getStatus().getPodIP();
  }

  public KubePodProcess(KubernetesClient client, String podName, String image, int stdoutLocalPort, boolean usesStdin)
      throws IOException, InterruptedException {
    this.client = client;

    // allow reading stdout from pod
    LOGGER.info("Creating socket server...");
    this.stdoutServerSocket = new ServerSocket(stdoutLocalPort);

    executorService = Executors.newSingleThreadExecutor();
    executorService.submit(() -> {
      try {
        LOGGER.info("Creating socket from server...");
        var socket = stdoutServerSocket.accept(); // blocks until connected
        LOGGER.info("Setting stdout...");
        this.stdout = socket.getInputStream();
      } catch (IOException e) {
        e.printStackTrace(); // todo: propagate exception / join at the end of constructor
      }
    });

    // create pod
    String entrypoint = getCommandFromImage(client, image);
    LOGGER.info("Found entrypoint: {}", entrypoint);

    Volume volume = new VolumeBuilder()
        .withName("airbyte-pipes")
        .withNewEmptyDir()
        .endEmptyDir()
        .build();

    VolumeMount volumeMount = new VolumeMountBuilder()
        .withName("airbyte-pipes")
        .withMountPath("/pipes")
        .build();

    Container initContainer = new ContainerBuilder()
        .withName("init")
        .withImage("busybox:1.28")
        .withCommand("sh", "-c", usesStdin ? "mkfifo /pipes/stdin && mkfifo /pipes/stdout" : "mkfifo /pipes/stdout")
        .withVolumeMounts(volumeMount)
        .build();

    Container main = new ContainerBuilder()
        .withName("main")
        .withImage(image)
        .withCommand("sh", "-c", usesStdin ? "cat /pipes/stdin | " + entrypoint + " > /pipes/stdout" : entrypoint + " > /pipes/stdout")
        .withVolumeMounts(volumeMount)
        .build();

    Container remoteStdin = new ContainerBuilder()
        .withName("remote-stdin")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", "socat -d -d -d TCP-L:9001 STDOUT > /pipes/stdin")
        .withVolumeMounts(volumeMount)
        .build();

    Container relayStdout = new ContainerBuilder()
        .withName("relay-stdout")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", "cat /pipes/stdout | socat -d -d -d - TCP:" + InetAddress.getLocalHost().getHostAddress() + ":" + stdoutLocalPort)
        .withVolumeMounts(volumeMount)
        .build();

    List<Container> containers = usesStdin ? List.of(main, remoteStdin, relayStdout) : List.of(main, relayStdout);

    Pod pod = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName(podName)
        .endMetadata()
        .withNewSpec()
        .withRestartPolicy("Never")
        .withInitContainers(initContainer)
        .withContainers(containers)
        .withVolumes(volume)
        .endSpec()
        .build();

    LOGGER.info("Creating pod...");
    this.podDefinition = client.pods().inNamespace("default").createOrReplace(pod);

    LOGGER.info("Waiting until pod is ready...");
    client.resource(podDefinition).waitUntilReady(5, TimeUnit.MINUTES);

    // allow writing stdin to pod
    LOGGER.info("Reading pod IP...");
    var podIp = getPodIP(client, podName);
    LOGGER.info("Pod IP: {}", podIp);

    if (usesStdin) {
      LOGGER.info("Creating stdin socket...");
      var socketToDestStdIo = new Socket(podIp, STDIN_REMOTE_PORT);
      this.stdin = socketToDestStdIo.getOutputStream();
    } else {
      LOGGER.info("Using null stdin output stream...");
      this.stdin = NullOutputStream.NULL_OUTPUT_STREAM;
    }
  }

  @Override
  public OutputStream getOutputStream() {
    return this.stdin;
  }

  @Override
  public InputStream getInputStream() {
    return this.stdout;
  }

  @Override
  public InputStream getErrorStream() {
    // there is no error stream equivalent for Kube-based processes so we use a null stream here
    return InputStream.nullInputStream();
  }

  @Override
  public int waitFor() throws InterruptedException {
    // These are closed in the opposite order in which they are created to prevent any resource conflicts.
    client.resource(podDefinition).waitUntilCondition(this::isTerminal, 10, TimeUnit.DAYS);
    try {
      this.stdin.close();
      this.stdoutServerSocket.close();
      this.stdout.close();
      this.executorService.shutdownNow();
    } catch (IOException e) {
      e.printStackTrace();
    }

    return exitValue();
  }

  private boolean isTerminal(Pod pod) {
    if (pod.getStatus() != null) {
      return pod.getStatus()
          .getContainerStatuses()
          .stream()
          .anyMatch(e -> e.getState() != null && e.getState().getTerminated() != null);
    } else {
      return false;
    }
  }

  private int getReturnCode(Pod pod) {
    Pod refreshedPod = client.pods().inNamespace("default").withName(pod.getMetadata().getName()).get();
    Preconditions.checkArgument(isTerminal(refreshedPod));

    return refreshedPod.getStatus().getContainerStatuses()
        .stream()
        .filter(containerStatus -> containerStatus.getState() != null && containerStatus.getState().getTerminated() != null)
        .map(containerStatus -> {
          int statusCode = containerStatus.getState().getTerminated().getExitCode();
          LOGGER.info("Termination status for container " + containerStatus.getName() + " is " + statusCode);
          return statusCode;
        })
        .reduce(Integer::sum)
        .orElseThrow();
  }

  @Override
  public int exitValue() {
    return getReturnCode(podDefinition);
  }

  @Override
  public void destroy() {
    try {
      stdoutServerSocket.close();
    } catch (IOException e) {
      throw new RuntimeException(e);
    } finally {
      executorService.shutdown();
      client.resource(podDefinition).withPropagationPolicy(DeletionPropagation.FOREGROUND).delete();
    }
  }

}
