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

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ResourceRequirements;
import io.fabric8.kubernetes.api.model.Container;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.Quantity;
import io.fabric8.kubernetes.api.model.ResourceRequirementsBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.internal.readiness.Readiness;
import io.kubernetes.client.Copy;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.ProcessHandle.Info;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.commons.io.output.NullOutputStream;
import org.apache.commons.text.StringEscapeUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * A Process abstraction backed by a Kube Pod running in a Kubernetes cluster 'somewhere'. The
 * parent process starting a Kube Pod Process needs to exist within the Kube networking space. This
 * is so the parent process can forward data into the child's stdin and read the child's stdout and
 * stderr streams and copy configuration files over.
 *
 * This is made possible by:
 * <li>1) An init container that creates 3 named pipes corresponding to stdin, stdout and std err on
 * a shared volume.</li>
 * <li>2) Config files (e.g. config.json, catalog.json etc) are copied from the parent process into
 * a shared volume.</li>
 * <li>3) Redirecting the stdin named pipe to the original image's entrypoint and it's output into
 * the respective named pipes for stdout and stderr.</li>
 * <li>4) Each named pipe has a corresponding side car. Each side car forwards its stream
 * accordingly using socat. e.g. stderr/stdout is forwarded to parent process while input from the
 * parent process is forwarded into stdin.</li>
 * <li>5) The parent process listens on the stdout and stederr sockets for an incoming TCP
 * connection. It also initiates a TCP connection to the child process aka the Kube pod on the
 * specified stdin socket.</li>
 * <li>6) The child process is able to access configuration data via the shared volume. It's inputs
 * and outputs - stdin, stdout and stderr - are forwarded the parent process via the sidecars.</li>
 * <li>7) The main process has its entrypoint wrapped to perform IO redirection and better error
 * handling.</li>
 * <li>8) A heartbeat sidecar checks if the worker that launched the pod is still alive. If not, the
 * pod will fail.</li>
 *
 * The docker image used for this pod process must expose a AIRBYTE_ENTRYPOINT which contains the
 * entrypoint we will wrap when creating the main container in the pod.
 *
 * See the constructor for more information.
 */

// TODO(Davin): Better test for this. See https://github.com/airbytehq/airbyte/issues/3700.
public class KubePodProcess extends Process {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcess.class);

  private static final String INIT_CONTAINER_NAME = "init";
  private static final Long STATUS_CHECK_INTERVAL_MS = 30 * 1000L;

  private static final String PIPES_DIR = "/pipes";
  private static final String STDIN_PIPE_FILE = PIPES_DIR + "/stdin";
  private static final String STDOUT_PIPE_FILE = PIPES_DIR + "/stdout";
  private static final String STDERR_PIPE_FILE = PIPES_DIR + "/stderr";
  private static final String CONFIG_DIR = "/config";
  private static final String TERMINATION_DIR = "/termination";
  private static final String TERMINATION_FILE_MAIN = TERMINATION_DIR + "/main";
  private static final String TERMINATION_FILE_CHECK = TERMINATION_DIR + "/check";
  private static final String SUCCESS_FILE_NAME = "FINISHED_UPLOADING";

  // 143 is the typical SIGTERM exit code.
  private static final int KILLED_EXIT_CODE = 143;
  private static final int STDIN_REMOTE_PORT = 9001;
  private static final Map<String, String> AIRBYTE_POD_LABELS = Map.of("airbyte", "worker-pod");

  private final KubernetesClient fabricClient;
  private final Pod podDefinition;
  // Necessary since it is not possible to retrieve the pod's actual exit code upon termination. This
  // is because the Kube API server does not keep
  // terminated pod history like it does for successful pods.
  // This variable should be set in functions where the pod is forcefully terminated. See
  // getReturnCode() for more info.
  private final AtomicBoolean wasKilled = new AtomicBoolean(false);

  private final OutputStream stdin;
  private InputStream stdout;
  private InputStream stderr;
  private Integer returnCode = null;
  private Long lastStatusCheck = null;

  private final ServerSocket stdoutServerSocket;
  private final int stdoutLocalPort;
  private final ServerSocket stderrServerSocket;
  private final int stderrLocalPort;
  private final ExecutorService executorService;

  public static String getPodIP(KubernetesClient client, String podName, String namespace) {
    var pod = client.pods().inNamespace(namespace).withName(podName).get();
    if (pod == null) {
      throw new RuntimeException("Error: unable to find pod!");
    }
    return pod.getStatus().getPodIP();
  }

  private static Container getInit(boolean usesStdin, List<VolumeMount> mainVolumeMounts) {
    var initEntrypointStr = String.format("mkfifo %s && mkfifo %s", STDOUT_PIPE_FILE, STDERR_PIPE_FILE);

    if (usesStdin) {
      initEntrypointStr = String.format("mkfifo %s && ", STDIN_PIPE_FILE) + initEntrypointStr;
    }

    initEntrypointStr = initEntrypointStr + String.format(" && until [ -f %s ]; do sleep 5; done;", SUCCESS_FILE_NAME);

    return new ContainerBuilder()
        .withName(INIT_CONTAINER_NAME)
        .withImage("busybox:1.28")
        .withWorkingDir(CONFIG_DIR)
        .withCommand("sh", "-c", initEntrypointStr)
        .withVolumeMounts(mainVolumeMounts)
        .build();
  }

  private static Container getMain(String image,
                                   boolean usesStdin,
                                   String entrypointOverride,
                                   List<VolumeMount> mainVolumeMounts,
                                   ResourceRequirements resourceRequirements,
                                   String[] args)
      throws IOException {
    var argsStr = String.join(" ", args);
    var optionalStdin = usesStdin ? String.format("cat %s | ", STDIN_PIPE_FILE) : "";
    var entrypointOverrideValue = entrypointOverride == null ? "" : StringEscapeUtils.escapeXSI(entrypointOverride);

    // communicates its completion to the heartbeat check via a file and closes itself if the heartbeat
    // fails
    var mainCommand = MoreResources.readResource("entrypoints/main.sh")
        .replaceAll("TERMINATION_FILE_CHECK", TERMINATION_FILE_CHECK)
        .replaceAll("TERMINATION_FILE_MAIN", TERMINATION_FILE_MAIN)
        .replaceAll("OPTIONAL_STDIN", optionalStdin)
        .replace("ENTRYPOINT_OVERRIDE_VALUE", entrypointOverrideValue) // use replace and not replaceAll to preserve escaping and quoting
        .replaceAll("ARGS", argsStr)
        .replaceAll("STDERR_PIPE_FILE", STDERR_PIPE_FILE)
        .replaceAll("STDOUT_PIPE_FILE", STDOUT_PIPE_FILE);

    final ContainerBuilder containerBuilder = new ContainerBuilder()
        .withName("main")
        .withImage(image)
        .withCommand("sh", "-c", mainCommand)
        .withWorkingDir(CONFIG_DIR)
        .withVolumeMounts(mainVolumeMounts);
    final ResourceRequirementsBuilder resourceRequirementsBuilder = getResourceRequirementsBuilder(resourceRequirements);
    if (resourceRequirementsBuilder != null) {
      containerBuilder.withResources(resourceRequirementsBuilder.build());
    }
    return containerBuilder.build();
  }

  private static void copyFilesToKubeConfigVolume(ApiClient officialClient, String podName, String namespace, Map<String, String> files) {
    List<Map.Entry<String, String>> fileEntries = new ArrayList<>(files.entrySet());

    // copy this file last to indicate that the copy has completed
    fileEntries.add(new AbstractMap.SimpleEntry<>(SUCCESS_FILE_NAME, ""));

    for (Map.Entry<String, String> file : fileEntries) {
      try {
        LOGGER.info("Uploading file: " + file.getKey());
        var contents = file.getValue().getBytes(StandardCharsets.UTF_8);
        var containerPath = Path.of(CONFIG_DIR + "/" + file.getKey());

        // fabric8 kube client upload doesn't work on gke:
        // https://github.com/fabric8io/kubernetes-client/issues/2217
        Copy copy = new Copy(officialClient);
        copy.copyFileToPod(namespace, podName, INIT_CONTAINER_NAME, contents, containerPath);

      } catch (IOException | ApiException e) {
        throw new RuntimeException(e);
      }
    }
  }

  /**
   * The calls in this function aren't straight-forward due to api limitations. There is no proper way
   * to directly look for containers within a pod or query if a container is in a running state beside
   * checking if the getRunning field is set. We could put this behind an interface, but that seems
   * heavy-handed compared to the 10 lines here.
   */
  private static void waitForInitPodToRun(KubernetesClient client, Pod podDefinition) throws InterruptedException {
    LOGGER.info("Waiting for init container to be ready before copying files...");
    client.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName())
        .waitUntilCondition(p -> p.getStatus().getInitContainerStatuses().size() != 0, 5, TimeUnit.MINUTES);
    LOGGER.info("Init container present..");
    client.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName())
        .waitUntilCondition(p -> p.getStatus().getInitContainerStatuses().get(0).getState().getRunning() != null, 5, TimeUnit.MINUTES);
    LOGGER.info("Init container ready..");
  }

  public KubePodProcess(String processRunnerHost,
                        ApiClient officialClient,
                        KubernetesClient fabricClient,
                        String podName,
                        String namespace,
                        String image,
                        int stdoutLocalPort,
                        int stderrLocalPort,
                        String kubeHeartbeatUrl,
                        boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypointOverride,
                        ResourceRequirements resourceRequirements,
                        final String... args)
      throws IOException, InterruptedException {
    this.fabricClient = fabricClient;
    this.stdoutLocalPort = stdoutLocalPort;
    this.stderrLocalPort = stderrLocalPort;

    stdoutServerSocket = new ServerSocket(stdoutLocalPort);
    stderrServerSocket = new ServerSocket(stderrLocalPort);
    executorService = Executors.newFixedThreadPool(2);
    setupStdOutAndStdErrListeners();

    if (entrypointOverride != null) {
      LOGGER.info("Found entrypoint override: {}", entrypointOverride);
    }

    Volume pipeVolume = new VolumeBuilder()
        .withName("airbyte-pipes")
        .withNewEmptyDir()
        .endEmptyDir()
        .build();

    VolumeMount pipeVolumeMount = new VolumeMountBuilder()
        .withName("airbyte-pipes")
        .withMountPath(PIPES_DIR)
        .build();

    Volume configVolume = new VolumeBuilder()
        .withName("airbyte-config")
        .withNewEmptyDir()
        .endEmptyDir()
        .build();

    VolumeMount configVolumeMount = new VolumeMountBuilder()
        .withName("airbyte-config")
        .withMountPath(CONFIG_DIR)
        .build();

    Volume terminationVolume = new VolumeBuilder()
        .withName("airbyte-termination")
        .withNewEmptyDir()
        .endEmptyDir()
        .build();

    VolumeMount terminationVolumeMount = new VolumeMountBuilder()
        .withName("airbyte-termination")
        .withMountPath(TERMINATION_DIR)
        .build();

    Container init = getInit(usesStdin, List.of(pipeVolumeMount, configVolumeMount));
    Container main = getMain(
        image,
        usesStdin,
        entrypointOverride,
        List.of(pipeVolumeMount, configVolumeMount, terminationVolumeMount),
        resourceRequirements,
        args);

    Container remoteStdin = new ContainerBuilder()
        .withName("remote-stdin")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", "socat -d -d -d TCP-L:9001 STDOUT > " + STDIN_PIPE_FILE)
        .withVolumeMounts(pipeVolumeMount, terminationVolumeMount)
        .build();

    Container relayStdout = new ContainerBuilder()
        .withName("relay-stdout")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", String.format("cat %s | socat -d -d -d - TCP:%s:%s", STDOUT_PIPE_FILE, processRunnerHost, stdoutLocalPort))
        .withVolumeMounts(pipeVolumeMount, terminationVolumeMount)
        .build();

    Container relayStderr = new ContainerBuilder()
        .withName("relay-stderr")
        .withImage("alpine/socat:1.7.4.1-r1")
        .withCommand("sh", "-c", String.format("cat %s | socat -d -d -d - TCP:%s:%s", STDERR_PIPE_FILE, processRunnerHost, stderrLocalPort))
        .withVolumeMounts(pipeVolumeMount, terminationVolumeMount)
        .build();

    // communicates via a file if it isn't able to reach the heartbeating server and succeeds if the
    // main container completes
    final String heartbeatCommand = MoreResources.readResource("entrypoints/check.sh")
        .replaceAll("TERMINATION_FILE_CHECK", TERMINATION_FILE_CHECK)
        .replaceAll("TERMINATION_FILE_MAIN", TERMINATION_FILE_MAIN)
        .replaceAll("HEARTBEAT_URL", kubeHeartbeatUrl);

    Container callHeartbeatServer = new ContainerBuilder()
        .withName("call-heartbeat-server")
        .withImage("curlimages/curl:7.77.0")
        .withCommand("sh")
        .withArgs("-c", heartbeatCommand)
        .withVolumeMounts(terminationVolumeMount)
        .build();

    List<Container> containers = usesStdin ? List.of(main, remoteStdin, relayStdout, relayStderr, callHeartbeatServer)
        : List.of(main, relayStdout, relayStderr, callHeartbeatServer);

    final Pod pod = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName(podName)
        .withLabels(AIRBYTE_POD_LABELS)
        .endMetadata()
        .withNewSpec()
        .withRestartPolicy("Never")
        .withInitContainers(init)
        .withContainers(containers)
        .withVolumes(pipeVolume, configVolume, terminationVolume)
        .endSpec()
        .build();

    LOGGER.info("Creating pod...");
    this.podDefinition = fabricClient.pods().inNamespace(namespace).createOrReplace(pod);

    waitForInitPodToRun(fabricClient, podDefinition);

    LOGGER.info("Copying files...");
    copyFilesToKubeConfigVolume(officialClient, podName, namespace, files);

    LOGGER.info("Waiting until pod is ready...");
    // If a pod gets into a non-terminal error state it should be automatically killed by our
    // heartbeating mechanism.
    // This also handles the case where a very short pod already completes before this check completes
    // the first time.
    // This doesn't manage things like pods that are blocked from running for some cluster reason or if
    // the init
    // container got stuck somehow.
    fabricClient.resource(podDefinition).waitUntilCondition(p -> {
      boolean isReady = Objects.nonNull(p) && Readiness.getInstance().isReady(p);
      return isReady || isTerminal(p);
    }, 10, TimeUnit.DAYS);

    // allow writing stdin to pod
    LOGGER.info("Reading pod IP...");
    var podIp = getPodIP(fabricClient, podName, namespace);
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
    var context = MDC.getCopyOfContextMap();
    executorService.submit(() -> {
      MDC.setContextMap(context);
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
      MDC.setContextMap(context);
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

  /**
   * Immediately terminates the Kube Pod backing this process and cleans up IO resources.
   */
  @Override
  public int waitFor() throws InterruptedException {
    Pod refreshedPod =
        fabricClient.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName()).get();
    fabricClient.resource(refreshedPod).waitUntilCondition(this::isTerminal, 10, TimeUnit.DAYS);
    wasKilled.set(true);
    return exitValue();
  }

  /**
   * Intended to gracefully clean up after a completed Kube Pod. This should only be called if the
   * process is successful.
   */
  @Override
  public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
    return super.waitFor(timeout, unit);
  }

  /**
   * Immediately terminates the Kube Pod backing this process and cleans up IO resources.
   */
  @Override
  public void destroy() {
    LOGGER.info("Destroying Kube process: {}", podDefinition.getMetadata().getName());
    try {
      fabricClient.resource(podDefinition).withPropagationPolicy(DeletionPropagation.FOREGROUND).delete();
      wasKilled.set(true);
    } finally {
      close();
      LOGGER.info("Destroyed Kube process: {}", podDefinition.getMetadata().getName());
    }
  }

  @Override
  public Info info() {
    return new KubePodProcessInfo(podDefinition.getMetadata().getName());
  }

  /**
   * Close all open resource in the opposite order of resource creation.
   *
   * Null checks exist because certain local Kube clusters (e.g. Docker for Desktop) back this
   * implementation with OS processes and resources, which are automatically reaped by the OS.
   */
  private void close() {
    if (this.stdin != null) {
      Exceptions.swallow(this.stdin::close);
    }
    if (this.stdout != null) {
      Exceptions.swallow(this.stdout::close);
    }
    if (this.stderr != null) {
      Exceptions.swallow(this.stderr::close);
    }
    Exceptions.swallow(this.stdoutServerSocket::close);
    Exceptions.swallow(this.stderrServerSocket::close);
    Exceptions.swallow(this.executorService::shutdownNow);

    KubePortManagerSingleton.offer(stdoutLocalPort);
    KubePortManagerSingleton.offer(stderrLocalPort);

    LOGGER.debug("Closed {}", podDefinition.getMetadata().getName());
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

  /**
   * This method hits the Kube Api server to retrieve statuses. Most of the complexity here is
   * minimising the api calls for performance.
   */
  private int getReturnCode(Pod pod) {
    if (returnCode != null) {
      return returnCode;
    }

    // Reuse the last status check result to prevent overloading the Kube Api server.
    if (lastStatusCheck != null && System.currentTimeMillis() - lastStatusCheck < STATUS_CHECK_INTERVAL_MS) {
      throw new IllegalThreadStateException("Kube pod process has not exited yet.");
    }

    var name = pod.getMetadata().getName();
    Pod refreshedPod = fabricClient.pods().inNamespace(pod.getMetadata().getNamespace()).withName(name).get();
    if (refreshedPod == null) {
      if (wasKilled.get()) {
        LOGGER.info("Unable to find pod {} to retrieve exit value. Defaulting to  value {}. This is expected if the job was cancelled.", name,
            KILLED_EXIT_CODE);
        return KILLED_EXIT_CODE;
      }
      // If the pod cannot be found and was not killed, it either means 1) the pod was not created
      // properly 2) this method is incorrectly called.
      throw new RuntimeException("Cannot find pod while trying to retrieve exit code. This probably means the Pod was not correctly created.");
    }

    if (!isTerminal(refreshedPod)) {
      lastStatusCheck = System.currentTimeMillis();
      throw new IllegalThreadStateException("Kube pod process has not exited yet.");
    }

    returnCode = refreshedPod.getStatus().getContainerStatuses()
        .stream()
        .filter(containerStatus -> containerStatus.getState() != null && containerStatus.getState().getTerminated() != null)
        .map(containerStatus -> {
          return containerStatus.getState().getTerminated().getExitCode();
        })
        .reduce(Integer::sum)
        .orElseThrow();

    LOGGER.info("Exit code for pod {} is {}", name, returnCode);
    return returnCode;
  }

  @Override
  public int exitValue() {
    // getReturnCode throws IllegalThreadException if the Kube pod has not exited;
    // close() is only called if the Kube pod has terminated.
    var returnCode = getReturnCode(podDefinition);
    // The OS traditionally handles process resource clean up. Therefore an exit code of 0, also
    // indicates that all kernel resources were shut down.
    // Because this is a custom implementation, manually close all the resources.
    // Further, since the local resources are used to talk to Kubernetes resources, shut local resources
    // down after Kubernetes resources are shut down, regardless of Kube termination status.
    close();
    LOGGER.info("Closed all resources for pod {}", podDefinition.getMetadata().getName());
    return returnCode;
  }

  private static ResourceRequirementsBuilder getResourceRequirementsBuilder(ResourceRequirements resourceRequirements) {
    if (resourceRequirements != null) {
      final Map<String, Quantity> requestMap = new HashMap<>();
      // if null then use unbounded resource allocation
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getCpuRequest())) {
        requestMap.put("cpu", Quantity.parse(resourceRequirements.getCpuRequest()));
      }
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getMemoryRequest())) {
        requestMap.put("memory", Quantity.parse(resourceRequirements.getMemoryRequest()));
      }
      final Map<String, Quantity> limitMap = new HashMap<>();
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getCpuLimit())) {
        limitMap.put("cpu", Quantity.parse(resourceRequirements.getCpuLimit()));
      }
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getMemoryLimit())) {
        limitMap.put("memory", Quantity.parse(resourceRequirements.getMemoryLimit()));
      }
      return new ResourceRequirementsBuilder()
          .withRequests(requestMap)
          .withLimits(limitMap);
    }
    return null;
  }

}
