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
import io.airbyte.commons.string.Strings;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A Process abstraction backed by a Kube Pod running in a Kubernetes cluster 'somewhere'. The
 * parent process starting a Kube Pod Process needs to exist within the Kube networking space. This
 * is so the parent process can forward data into the child's stdin and read the child's stdout and
 * stderr streams.
 *
 * This is made possible by:
 * <li>1) An init container that creates 3 named pipes corresponding to stdin, stdout and std err.
 * </li>
 * <li>2) Redirecting the stdin named pipe to the original image's entrypoint and it's output into
 * the respective named pipes for stdout and stderr.</li>
 * <li>3) Each named pipe has a corresponding side car. Each side car forwards its stream
 * accordingly using socat. e.g. stderr/stdout is forwarded to parent process while input from the
 * parent process is forwarded into stdin.</li>
 * <li>4) The parent process listens on the stdout and stederr sockets for an incoming TCP
 * connection. It also initiates a TCP connection to the child process aka the Kube pod on the
 * specified stdin socket.</li>
 *
 * See the constructor for more information.
 */

// TODO(Davin): Better test for this. See https://github.com/airbytehq/airbyte/issues/3700.
public class KubePodProcess extends Process {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcess.class);

  private static final int STDIN_REMOTE_PORT = 9001;

  private final KubernetesClient client;
  private final Pod podDefinition;

  private final OutputStream stdin;
  private InputStream stdout;
  private InputStream stderr;

  private final ServerSocket stdoutServerSocket;
  private final ServerSocket stderrServerSocket;
  private final ExecutorService executorService;

  // TODO(Davin): Cache this result.
  public static String getCommandFromImage(KubernetesClient client, String imageName, String namespace) throws InterruptedException {
    final String podName = Strings.addRandomSuffix("airbyte-command-fetcher", "-", 5);

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
    Pod podDefinition = client.pods().inNamespace(namespace).createOrReplace(pod);
    LOGGER.info("Waiting until command fetcher pod completes...");
    // TODO(Davin): If a pod is not missing, this will wait for up to 2 minutes before error-ing out.
    // Figure out a better way.
    client.resource(podDefinition).waitUntilCondition(p -> p.getStatus().getPhase().equals("Succeeded"), 2, TimeUnit.MINUTES);

    var logs = client.pods().inNamespace(namespace).withName(podName).getLog();
    if (!logs.contains("AIRBYTE_ENTRYPOINT")) {
      throw new RuntimeException(
          "Missing AIRBYTE_ENTRYPOINT from command fetcher logs. This should not happen. Check the echo command has not been changed.");
    }

    var envVal = logs.split("=")[1].strip();
    if (envVal.isEmpty()) {
      // default to returning default entrypoint in bases
      return "/airbyte/base.sh";
    }

    return envVal;
  }

  public static String getPodIP(KubernetesClient client, String podName, String namespace) {
    var pod = client.pods().inNamespace(namespace).withName(podName).get();
    if (pod == null) {
      throw new RuntimeException("Error: unable to find pod!");
    }
    return pod.getStatus().getPodIP();
  }

  public KubePodProcess(KubernetesClient client,
                        String podName,
                        String namespace,
                        String image,
                        int stdoutLocalPort,
                        int stderrLocalPort,
                        boolean usesStdin)
      throws IOException, InterruptedException {
    this.client = client;

    stdoutServerSocket = new ServerSocket(stdoutLocalPort);
    stderrServerSocket = new ServerSocket(stderrLocalPort);
    executorService = Executors.newFixedThreadPool(2);
    setupStdOutAndStdErrListeners();

    String entrypoint = getCommandFromImage(client, image, namespace);
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
        .withCommand("sh", "-c",
            usesStdin ? "mkfifo /pipes/stdin && mkfifo /pipes/stdout && mkfifo /pipes/stderr" : "mkfifo /pipes/stdout && mkfifo /pipes/stderr")
        .withVolumeMounts(volumeMount)
        .build();

    Container main = new ContainerBuilder()
        .withName("main")
        .withImage(image)
        .withCommand("sh", "-c",
            usesStdin ? "cat /pipes/stdin | " + entrypoint + " 2> /pipes/stderr > /pipes/stdout" : entrypoint + "   2> /pipes/stderr > /pipes/stdout")
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

    Container relayStderr = new ContainerBuilder()
        .withName("relay-stderr")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", "cat /pipes/stderr | socat -d -d -d - TCP:" + InetAddress.getLocalHost().getHostAddress() + ":" + stderrLocalPort)
        .withVolumeMounts(volumeMount)
        .build();

    List<Container> containers = usesStdin ? List.of(main, remoteStdin, relayStdout, relayStderr) : List.of(main, relayStdout, relayStderr);

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
    this.podDefinition = client.pods().inNamespace(namespace).createOrReplace(pod);

    LOGGER.info("Waiting until pod is ready...");
    client.resource(podDefinition).waitUntilReady(5, TimeUnit.MINUTES);

    // allow writing stdin to pod
    LOGGER.info("Reading pod IP...");
    var podIp = getPodIP(client, podName, namespace);
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

  private void setupStdOutAndStdErrListeners() {
    executorService.submit(() -> {
      try {
        LOGGER.info("Creating stdout socket server...");
        var socket = stdoutServerSocket.accept(); // blocks until connected
        LOGGER.info("Setting stdout...");
        this.stdout = socket.getInputStream();
      } catch (IOException e) {
        e.printStackTrace(); // todo: propagate exception / join at the end of constructor
      }
    });
    executorService.submit(() -> {
      try {
        LOGGER.info("Creating stderr socket server...");
        var socket = stderrServerSocket.accept(); // blocks until connected
        LOGGER.info("Setting stderr...");
        this.stderr = socket.getInputStream();
      } catch (IOException e) {
        e.printStackTrace(); // todo: propagate exception / join at the end of constructor
      }
    });
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
    return this.stderr;
  }

  @Override
  public int waitFor() throws InterruptedException {
    // These are closed in the opposite order in which they are created to prevent any resource
    // conflicts.
    client.resource(podDefinition).waitUntilCondition(this::isTerminal, 10, TimeUnit.DAYS);
    try {
      this.stdin.close();
      this.stdout.close();
      this.stdoutServerSocket.close();
      this.stderr.close();
      this.stderrServerSocket.close();
    } catch (IOException e) {
      LOGGER.warn("Error while closing sockets and streams: ", e);
      throw new InterruptedException();
    }
    this.executorService.shutdownNow();

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
    Pod refreshedPod = client.pods().inNamespace(pod.getMetadata().getNamespace()).withName(pod.getMetadata().getName()).get();
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
