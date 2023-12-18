package io.airbyte.integrations.source_performance;

import com.google.common.base.Strings;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.TolerationPOJO;
import io.airbyte.workers.process.ExitCodeWatcher;
import io.airbyte.workers.process.KubeContainerInfo;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.KubePodProcessInfo;
import io.airbyte.workers.process.KubePodResourceHelper;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.fabric8.kubernetes.api.model.Affinity;
import io.fabric8.kubernetes.api.model.AffinityBuilder;
import io.fabric8.kubernetes.api.model.Container;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.ContainerPort;
import io.fabric8.kubernetes.api.model.ContainerPortBuilder;
import io.fabric8.kubernetes.api.model.ContainerStatus;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.EnvVar;
import io.fabric8.kubernetes.api.model.EnvVarSource;
import io.fabric8.kubernetes.api.model.LabelSelector;
import io.fabric8.kubernetes.api.model.LabelSelectorBuilder;
import io.fabric8.kubernetes.api.model.LabelSelectorRequirement;
import io.fabric8.kubernetes.api.model.LabelSelectorRequirementBuilder;
import io.fabric8.kubernetes.api.model.LocalObjectReference;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodAffinity;
import io.fabric8.kubernetes.api.model.PodAffinityBuilder;
import io.fabric8.kubernetes.api.model.PodAffinityTerm;
import io.fabric8.kubernetes.api.model.PodAffinityTermBuilder;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.PodFluent;
import io.fabric8.kubernetes.api.model.Quantity;
import io.fabric8.kubernetes.api.model.ResourceRequirementsBuilder;
import io.fabric8.kubernetes.api.model.Toleration;
import io.fabric8.kubernetes.api.model.TolerationBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeFluent;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.CascadingDeletable;
import io.fabric8.kubernetes.client.dsl.NonNamespaceOperation;
import io.fabric8.kubernetes.client.dsl.PodResource;
import io.fabric8.kubernetes.client.informers.SharedIndexInformer;
import io.fabric8.kubernetes.client.internal.readiness.Readiness;
import org.apache.commons.io.output.NullOutputStream;
import org.apache.commons.text.StringEscapeUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Path;
import java.time.Duration;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;

public class KubePodProcess2 {
  private static final Configs configs = new EnvConfigs();
  private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcess.class);
  public static final String MAIN_CONTAINER_NAME = "main";
  public static final String INIT_CONTAINER_NAME = "init";
  private static final ResourceRequirements DEFAULT_SIDECAR_RESOURCES;
  private static final ResourceRequirements DEFAULT_SOCAT_RESOURCES;
  private static final ResourceRequirements FAST_STDOUT_RESOURCES ;
  private static final String PIPES_DIR = "/pipes";
  private static final String STDIN_PIPE_FILE = "/pipes/stdin";
  private static final String STDOUT_PIPE_FILE = "/pipes/stdout";
  private static final String STDERR_PIPE_FILE = "/pipes/stderr";
  public static final String CONFIG_DIR = "/config";
  public static final String TMP_DIR = "/tmp";
  private static final String TERMINATION_DIR = "/termination";
  private static final String TERMINATION_FILE_MAIN = "/termination/main";
  private static final String TERMINATION_FILE_CHECK = "/termination/check";
  public static final String SUCCESS_FILE_NAME = "FINISHED_UPLOADING";
  private static final int STDIN_REMOTE_PORT = 9001;
  private static final int KILLED_EXIT_CODE = 143;
  private static final double INIT_SLEEP_PERIOD_SECONDS = 0.1;
  private static final Duration INIT_RETRY_TIMEOUT_MINUTES;
  private static final int INIT_RETRY_MAX_ITERATIONS;
  private final KubernetesClient fabricClient;
  private final Pod podDefinition;
  private final AtomicBoolean wasClosed = new AtomicBoolean(false);
  private final OutputStream stdin;
  private InputStream stdout;
  private InputStream stderr;
  private final ServerSocket stdoutServerSocket;
  private final int stdoutLocalPort;
  private final ServerSocket stderrServerSocket;
  private final int stderrLocalPort;
  private final ExecutorService executorService;
  private final CompletableFuture<Integer> exitCodeFuture;
  private final SharedIndexInformer<Pod> podInformer;

  public static String getPodIP(KubernetesClient client, String podName, String podNamespace) {
    Pod pod = (Pod)((PodResource)((NonNamespaceOperation)client.pods().inNamespace(podNamespace)).withName(podName)).get();
    if (pod == null) {
      throw new RuntimeException(prependPodInfo("Error: unable to find pod!", podNamespace, podName));
    } else {
      return pod.getStatus().getPodIP();
    }
  }

  private static Container getInit(boolean usesStdin, List<VolumeMount> mainVolumeMounts, String busyboxImage) throws IOException {
    String initCommand = MoreResources.readResource("entrypoints/sync/init.sh").replaceAll("USES_STDIN_VALUE", String.valueOf(usesStdin)).replaceAll("STDOUT_PIPE_FILE_VALUE", "/pipes/stdout").replaceAll("STDERR_PIPE_FILE_VALUE", "/pipes/stderr").replaceAll("STDIN_PIPE_FILE_VALUE", "/pipes/stdin").replaceAll("MAX_ITERATION_VALUE", String.valueOf(INIT_RETRY_MAX_ITERATIONS)).replaceAll("SUCCESS_FILE_NAME_VALUE", "FINISHED_UPLOADING").replaceAll("SLEEP_PERIOD_VALUE", String.valueOf(0.1));
    return ((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("init")).withImage(busyboxImage)).withWorkingDir("/config")).withCommand(new String[]{"sh", "-c", initCommand})).withResources(getResourceRequirementsBuilder(DEFAULT_SIDECAR_RESOURCES).build())).withVolumeMounts(mainVolumeMounts)).build();
  }

  private static Container getMain(String image, String imagePullPolicy, boolean usesStdin, String entrypointOverride, List<VolumeMount> mainVolumeMounts, ResourceRequirements resourceRequirements, Map<Integer, Integer> internalToExternalPorts, Map<String, String> envMap, String... args) throws IOException {
    String argsStr = String.join(" ", args);
    String optionalStdin = usesStdin ? String.format("< %s", "/pipes/stdin") : "";
    String entrypointOverrideValue = entrypointOverride == null ? "" : StringEscapeUtils.escapeXSI(entrypointOverride);
    String mainCommand = MoreResources.readResource("entrypoints/sync/main.sh").replaceAll("TERMINATION_FILE_CHECK", "/termination/check").replaceAll("TERMINATION_FILE_MAIN", "/termination/main").replaceAll("OPTIONAL_STDIN", optionalStdin).replace("ENTRYPOINT_OVERRIDE_VALUE", entrypointOverrideValue).replaceAll("ARGS", argsStr).replaceAll("STDERR_PIPE_FILE", "/pipes/stderr").replaceAll("STDOUT_PIPE_FILE", "/pipes/stdout");
    List<ContainerPort> containerPorts = createContainerPortList(internalToExternalPorts);
    List<EnvVar> envVars = (List)envMap.entrySet().stream().map((entry) -> {
      return new EnvVar((String)entry.getKey(), (String)entry.getValue(), (EnvVarSource)null);
    }).collect(Collectors.toList());
    ContainerBuilder containerBuilder = (ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("main")).withPorts(containerPorts)).withImage(image)).withImagePullPolicy(imagePullPolicy)).withCommand(new String[]{"sh", "-c", mainCommand})).withEnv(envVars)).withWorkingDir("/config")).withVolumeMounts(mainVolumeMounts);
    ResourceRequirementsBuilder resourceRequirementsBuilder = getResourceRequirementsBuilder(resourceRequirements);
    if (resourceRequirementsBuilder != null) {
      containerBuilder.withResources(resourceRequirementsBuilder.build());
    }

    return containerBuilder.build();
  }

  public static List<ContainerPort> createContainerPortList(Map<Integer, Integer> internalToExternalPorts) {
    return (List)internalToExternalPorts.keySet().stream().map((integer) -> {
      return ((ContainerPortBuilder)(new ContainerPortBuilder()).withContainerPort(integer)).build();
    }).collect(Collectors.toList());
  }

  public static void copyFilesToKubeConfigVolume(KubernetesClient client, Pod podDefinition, Map<String, String> files) {
    List<Map.Entry<String, String>> fileEntries = new ArrayList(files.entrySet());
    fileEntries.add(new AbstractMap.SimpleEntry("FINISHED_UPLOADING", ""));
    Path tmpFile = null;
    Process proc = null;
    Iterator var6 = fileEntries.iterator();

    while(var6.hasNext()) {
      Map.Entry<String, String> file = (Map.Entry)var6.next();

      try {
        tmpFile = Path.of(IOs.writeFileToRandomTmpDir((String)file.getKey(), (String)file.getValue()));
        LOGGER.info("Uploading file: " + (String)file.getKey());
        Path containerPath = Path.of("/config/" + (String)file.getKey());
        String command = String.format("kubectl cp %s %s/%s:%s -c %s", tmpFile, podDefinition.getMetadata().getNamespace(), podDefinition.getMetadata().getName(), containerPath, "init");
        LOGGER.info(command);
        proc = Runtime.getRuntime().exec(command);
        LOGGER.info("Waiting for kubectl cp to complete");
        int exitCode = proc.waitFor();
        if (exitCode != 0) {
          if (!"FINISHED_UPLOADING".equals(file.getKey()) || waitForInitPodToTerminate(client, podDefinition, 5L, TimeUnit.MINUTES) != 0) {
            throw new IOException("kubectl cp failed with exit code " + exitCode);
          }

          LOGGER.info("Init was successful; ignoring non-zero kubectl cp exit code for success indicator file.");
        }

        LOGGER.info("kubectl cp complete, closing process");
      } catch (InterruptedException | IOException var18) {
        throw new RuntimeException(var18);
      } finally {
        if (tmpFile != null) {
          try {
            tmpFile.toFile().delete();
          } catch (Exception var17) {
            LOGGER.info("Caught exception when deleting temp file but continuing to allow process deletion.", var17);
          }
        }

        if (proc != null) {
          proc.destroy();
        }

      }
    }

  }

  private static void waitForInitPodToRun(final KubernetesClient client, final Pod podDefinition) throws InterruptedException {
    // todo: this could use the watcher instead of waitUntilConditions
    LOGGER.info("Waiting for init container to be ready before copying files...");
    client.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName())
        .waitUntilCondition(p -> !p.getStatus().getInitContainerStatuses().isEmpty()
                && p.getStatus().getInitContainerStatuses().get(0).getState().getRunning() != null, Duration.ofMinutes(3).toMinutes(),
            TimeUnit.MINUTES);
    LOGGER.info("Init container ready..");
  }

  /**
   * Waits for the init container to terminate, and returns its exit code.
   */
  private static int waitForInitPodToTerminate(final KubernetesClient client,
                                               final Pod podDefinition,
                                               final long timeUnitsToWait,
                                               final TimeUnit timeUnit)
      throws InterruptedException {
    LOGGER.info("Waiting for init container to terminate before checking exit value...");
    client.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName())
        .waitUntilCondition(p -> p.getStatus().getInitContainerStatuses().get(0).getState().getTerminated() != null, timeUnitsToWait, timeUnit);
    final int exitValue = client.pods().inNamespace(podDefinition.getMetadata().getNamespace()).withName(podDefinition.getMetadata().getName()).get()
        .getStatus().getInitContainerStatuses().get(0).getState().getTerminated().getExitCode();
    LOGGER.info("Init container terminated with exit value {}.", exitValue);
    return exitValue;
  }

  private Toleration[] buildPodTolerations(List<TolerationPOJO> tolerations) {
    return tolerations != null && !tolerations.isEmpty() ? (Toleration[])tolerations.stream().map((workerPodToleration) -> {
      return ((TolerationBuilder)((TolerationBuilder)((TolerationBuilder)((TolerationBuilder)(new TolerationBuilder()).withKey(workerPodToleration.getKey())).withEffect(workerPodToleration.getEffect())).withOperator(workerPodToleration.getOperator())).withValue(workerPodToleration.getValue())).build();
    }).toArray((x$0) -> {
      return new Toleration[x$0];
    }) : null;
  }

  public KubePodProcess2(boolean isOrchestrator, String processRunnerHost, KubernetesClient fabricClient, String podName, String namespace, String image, String imagePullPolicy, String sidecarImagePullPolicy, int stdoutLocalPort, int stderrLocalPort, String kubeHeartbeatUrl, boolean usesStdin, Map<String, String> files, String entrypointOverride, ResourceRequirements resourceRequirements, List<String> imagePullSecrets, List<TolerationPOJO> tolerations, Map<String, String> nodeSelectors, Map<String, String> labels, Map<String, String> annotations, String socatImage, String busyboxImage, String curlImage, Map<String, String> envMap, Map<Integer, Integer> internalToExternalPorts, String... args) throws IOException, InterruptedException {
    this.fabricClient = fabricClient;
    this.stdoutLocalPort = stdoutLocalPort;
    this.stderrLocalPort = stderrLocalPort;
    this.stdoutServerSocket = new ServerSocket(stdoutLocalPort);
    this.stderrServerSocket = new ServerSocket(stderrLocalPort);
    this.executorService = Executors.newFixedThreadPool(2);
    this.setupStdOutAndStdErrListeners();
    if (entrypointOverride != null) {
      LOGGER.info("Found entrypoint override: {}", entrypointOverride);
    }

    Volume pipeVolume = ((VolumeBuilder)((VolumeBuilder)(new VolumeBuilder()).withName("airbyte-pipes")).withNewEmptyDir().endEmptyDir()).build();
    VolumeMount pipeVolumeMount = ((VolumeMountBuilder)((VolumeMountBuilder)(new VolumeMountBuilder()).withName("airbyte-pipes")).withMountPath("/pipes")).build();
    Volume configVolume = ((VolumeBuilder)((VolumeFluent.EmptyDirNested)((VolumeBuilder)(new VolumeBuilder()).withName("airbyte-config")).withNewEmptyDir().withMedium("Memory")).endEmptyDir()).build();
    VolumeMount configVolumeMount = ((VolumeMountBuilder)((VolumeMountBuilder)(new VolumeMountBuilder()).withName("airbyte-config")).withMountPath("/config")).build();
    Volume terminationVolume = ((VolumeBuilder)((VolumeBuilder)(new VolumeBuilder()).withName("airbyte-termination")).withNewEmptyDir().endEmptyDir()).build();
    VolumeMount terminationVolumeMount = ((VolumeMountBuilder)((VolumeMountBuilder)(new VolumeMountBuilder()).withName("airbyte-termination")).withMountPath("/termination")).build();
    Volume tmpVolume = ((VolumeBuilder)((VolumeBuilder)(new VolumeBuilder()).withName("tmp")).withNewEmptyDir().endEmptyDir()).build();
    VolumeMount tmpVolumeMount = ((VolumeMountBuilder)((VolumeMountBuilder)(new VolumeMountBuilder()).withName("tmp")).withMountPath("/tmp")).build();
    Container init = getInit(usesStdin, List.of(pipeVolumeMount, configVolumeMount), busyboxImage);
    Container main = getMain(image, imagePullPolicy, usesStdin, entrypointOverride, List.of(pipeVolumeMount, configVolumeMount, terminationVolumeMount, tmpVolumeMount), resourceRequirements, internalToExternalPorts, envMap, args);
    io.fabric8.kubernetes.api.model.ResourceRequirements heartbeatSidecarResources = getResourceRequirementsBuilder(DEFAULT_SIDECAR_RESOURCES).build();
    io.fabric8.kubernetes.api.model.ResourceRequirements socatSidecarResources = getResourceRequirementsBuilder(DEFAULT_SOCAT_RESOURCES).build();
    io.fabric8.kubernetes.api.model.ResourceRequirements fastSidecarResources = getResourceRequirementsBuilder(FAST_STDOUT_RESOURCES).build();

    Container remoteStdin = ((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("remote-stdin")).withImage(socatImage)).withCommand(new String[]{"sh", "-c", "socat -d -d TCP-L:9001 STDOUT > /pipes/stdin"})).withVolumeMounts(new VolumeMount[]{pipeVolumeMount, terminationVolumeMount})).withResources(socatSidecarResources)).withImagePullPolicy(sidecarImagePullPolicy)).build();
    Container relayStdout = ((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("relay-stdout")).withImage(socatImage)).withCommand(new String[]{"sh", "-c", String.format("cat %s | socat -d -d -t 60 - TCP:%s:%s", "/pipes/stdout", processRunnerHost, stdoutLocalPort)})).withVolumeMounts(new VolumeMount[]{pipeVolumeMount, terminationVolumeMount})).withResources(fastSidecarResources)).withImagePullPolicy(sidecarImagePullPolicy)).build();
    Container relayStderr = ((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("relay-stderr")).withImage(socatImage)).withCommand(new String[]{"sh", "-c", String.format("cat %s | socat -d -d -t 60 - TCP:%s:%s", "/pipes/stderr", processRunnerHost, stderrLocalPort)})).withVolumeMounts(new VolumeMount[]{pipeVolumeMount, terminationVolumeMount})).withResources(socatSidecarResources)).withImagePullPolicy(sidecarImagePullPolicy)).build();
    String heartbeatCommand = MoreResources.readResource("entrypoints/sync/check.sh").replaceAll("TERMINATION_FILE_CHECK", "/termination/check").replaceAll("TERMINATION_FILE_MAIN", "/termination/main").replaceAll("HEARTBEAT_URL", kubeHeartbeatUrl);
    Container callHeartbeatServer = ((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)((ContainerBuilder)(new ContainerBuilder()).withName("call-heartbeat-server")).withImage(curlImage)).withCommand(new String[]{"sh"})).withArgs(new String[]{"-c", heartbeatCommand})).withVolumeMounts(new VolumeMount[]{terminationVolumeMount})).withResources(heartbeatSidecarResources)).withImagePullPolicy(sidecarImagePullPolicy)).build();
    List<Container> containers = usesStdin ? List.of(main, remoteStdin, relayStdout, relayStderr, callHeartbeatServer) : List.of(main, relayStdout, relayStderr, callHeartbeatServer);
    PodFluent.SpecNested<PodBuilder> podBuilder = ((PodBuilder)((PodFluent.MetadataNested)((PodFluent.MetadataNested)((PodFluent.MetadataNested)((PodBuilder)(new PodBuilder()).withApiVersion("v1")).withNewMetadata().withName(podName)).withLabels(labels)).withAnnotations(annotations)).endMetadata()).withNewSpec();
    if (isOrchestrator) {
      podBuilder = (PodFluent.SpecNested)((PodFluent.SpecNested)podBuilder.withServiceAccount("airbyte-admin")).withAutomountServiceAccountToken(true);
    }

    List<LocalObjectReference> pullSecrets = (List)imagePullSecrets.stream().map((imagePullSecret) -> {
      return new LocalObjectReference(imagePullSecret);
    }).collect(Collectors.toList());

    LabelSelectorRequirement requirement = new LabelSelectorRequirementBuilder()
        .withKey("app")
        .withOperator("In")
        .withValues("destination-harness")
        .build();

    LabelSelector labelSelector = new LabelSelectorBuilder()
        .withMatchExpressions(Collections.singletonList(requirement))
        .build();

    PodAffinityTerm podAffinityTerm = new PodAffinityTermBuilder()
        .withLabelSelector(labelSelector)
        .withTopologyKey("kubernetes.io/hostname")
        .build();

    PodAffinity podAffinity = new PodAffinityBuilder()
        .withRequiredDuringSchedulingIgnoredDuringExecution(Collections.singletonList(podAffinityTerm))
        .build();

    Affinity affinity = new AffinityBuilder()
        .withPodAffinity(podAffinity)
        .build();

    final Pod pod = podBuilder.withTolerations(buildPodTolerations(tolerations))
        .withImagePullSecrets(pullSecrets) // An empty list or an empty LocalObjectReference turns this into a no-op setting.
        .withNodeSelector(nodeSelectors)
        .withRestartPolicy("Never")
        .withInitContainers(init)
        .withContainers(containers)
        .withAffinity(affinity)
        .withVolumes(pipeVolume, configVolume, terminationVolume, tmpVolume)
        .endSpec()
        .build();

    LOGGER.info("Creating pod with affinity 2 {}...", pod.getMetadata().getName());
    long start = System.currentTimeMillis();
    this.podDefinition = (Pod)((NonNamespaceOperation)fabricClient.pods().inNamespace(namespace)).createOrReplace(new Pod[]{pod});
    this.exitCodeFuture = new CompletableFuture();
    this.podInformer = ((PodResource)((NonNamespaceOperation)fabricClient.pods().inNamespace(namespace)).withName(pod.getMetadata().getName())).inform();
    SharedIndexInformer var10000 = this.podInformer;
    String var10003 = pod.getMetadata().getName();
    CompletableFuture var10005 = this.exitCodeFuture;
    Objects.requireNonNull(var10005);
    var10000.addEventHandler(new ExitCodeWatcher(var10003, namespace, var10005::complete, () -> {
      LOGGER.info(prependPodInfo(String.format("Exit code watcher failed to retrieve the exit code. Defaulting to %s. This is expected if the job was cancelled.", 143), namespace, podName));
      this.exitCodeFuture.complete(143);
    }));
    waitForInitPodToRun(fabricClient, this.podDefinition);
    LOGGER.info("Copying files...");
    copyFilesToKubeConfigVolume(fabricClient, this.podDefinition, files);
    LOGGER.info("Waiting until pod is ready...");
    fabricClient.resource(this.podDefinition).waitUntilCondition((p) -> {
      boolean isReady = Objects.nonNull(p) && Readiness.getInstance().isReady(p);
      return isReady || KubePodResourceHelper.isTerminal(p);
    }, 20L, TimeUnit.MINUTES)
    ;
    LOGGER.info("Reading pod IP...");
    String podIp = getPodIP(fabricClient, podName, namespace);
    LOGGER.info("Pod IP: {}", podIp);
    if (usesStdin) {
      LOGGER.info("Creating stdin socket...");
      Socket socketToDestStdIo = new Socket(podIp, 9001);
      this.stdin = socketToDestStdIo.getOutputStream();
    } else {
      LOGGER.info("Using null stdin output stream...");
      this.stdin = NullOutputStream.NULL_OUTPUT_STREAM;
    }

  }

  private void setupStdOutAndStdErrListeners() {
    Map<String, String> context = MDC.getCopyOfContextMap();
    this.executorService.submit(() -> {
      MDC.setContextMap(context);

      try {
        LOGGER.info("Creating stdout socket server...");
        Socket socket = this.stdoutServerSocket.accept();
        socket.setKeepAlive(true);
        LOGGER.info("Setting stdout...");
        this.stdout = socket.getInputStream();
      } catch (IOException var3) {
        var3.printStackTrace();
      }

    });
    this.executorService.submit(() -> {
      MDC.setContextMap(context);

      try {
        LOGGER.info("Creating stderr socket server...");
        Socket socket = this.stderrServerSocket.accept();
        socket.setKeepAlive(true);
        LOGGER.info("Setting stderr...");
        this.stderr = socket.getInputStream();
      } catch (IOException var3) {
        var3.printStackTrace();
      }

    });
  }

  public int waitFor() throws InterruptedException {
    try {
      this.exitCodeFuture.get();
    } catch (ExecutionException var2) {
      throw new RuntimeException(var2);
    }

    return this.exitValue();
  }

  public void destroy() {
    String podName = this.podDefinition.getMetadata().getName();
    String podNamespace = this.podDefinition.getMetadata().getNamespace();
    LOGGER.info(prependPodInfo("Destroying Kube process.", podNamespace, podName));

    try {
      ((CascadingDeletable)this.fabricClient.resource(this.podDefinition).withPropagationPolicy(DeletionPropagation.FOREGROUND)).delete();
      this.exitCodeFuture.complete(143);
    } finally {
      this.close();
      LOGGER.info(prependPodInfo("Destroyed Kube process.", podNamespace, podName));
    }

  }

  private Container getMainContainerFromPodDefinition() {
    Optional<Container> containerOptional = this.podDefinition.getSpec().getContainers().stream().filter((c) -> {
      return "main".equals(c.getName());
    }).findFirst();
    if (containerOptional.isEmpty()) {
      LOGGER.warn(String.format("Could not find main container definition for pod: %s", this.podDefinition.getMetadata().getName()));
      return null;
    } else {
      return (Container)containerOptional.get();
    }
  }

  public KubePodInfo getInfo() {
    Container mainContainer = this.getMainContainerFromPodDefinition();
    KubeContainerInfo mainContainerInfo = new KubeContainerInfo(mainContainer.getImage(), mainContainer.getImagePullPolicy());
    return new KubePodInfo(this.podDefinition.getMetadata().getNamespace(), this.podDefinition.getMetadata().getName(), mainContainerInfo);
  }

  private void close() {
    boolean previouslyClosed = this.wasClosed.getAndSet(true);
    if (!previouslyClosed) {
      if (this.stdin != null) {
        OutputStream var10000 = this.stdin;
        Objects.requireNonNull(var10000);
        Exceptions.swallow(var10000::close);
      }

      InputStream var2;
      if (this.stdout != null) {
        var2 = this.stdout;
        Objects.requireNonNull(var2);
        Exceptions.swallow(var2::close);
      }

      if (this.stderr != null) {
        var2 = this.stderr;
        Objects.requireNonNull(var2);
        Exceptions.swallow(var2::close);
      }

      ServerSocket var3 = this.stdoutServerSocket;
      Objects.requireNonNull(var3);
      Exceptions.swallow(var3::close);
      var3 = this.stderrServerSocket;
      Objects.requireNonNull(var3);
      Exceptions.swallow(var3::close);
      SharedIndexInformer var4 = this.podInformer;
      Objects.requireNonNull(var4);
      Exceptions.swallow(var4::close);
      ExecutorService var5 = this.executorService;
      Objects.requireNonNull(var5);
      Exceptions.swallow(var5::shutdownNow);
      KubePortManagerSingleton.getInstance().offer(this.stdoutLocalPort);
      KubePortManagerSingleton.getInstance().offer(this.stderrLocalPort);
      LOGGER.info(prependPodInfo("Closed all resources for pod", this.podDefinition.getMetadata().getNamespace(), this.podDefinition.getMetadata().getName()));
    }
  }

  private int getReturnCode() {
    if (this.exitCodeFuture.isDone()) {
      try {
        return (Integer)this.exitCodeFuture.get();
      } catch (ExecutionException | InterruptedException var2) {
        throw new RuntimeException(prependPodInfo("Cannot find pod %s : %s while trying to retrieve exit code. This probably means the pod was not correctly created.", this.podDefinition.getMetadata().getNamespace(), this.podDefinition.getMetadata().getName()), var2);
      }
    } else {
      throw new IllegalThreadStateException(prependPodInfo("Main container in kube pod has not terminated yet.", this.podDefinition.getMetadata().getNamespace(), this.podDefinition.getMetadata().getName()));
    }
  }

  public int exitValue() {
    int returnCode = this.getReturnCode();
    this.close();
    return returnCode;
  }

  public Process toProcess() {
    return new Process() {
      public OutputStream getOutputStream() {
        return KubePodProcess2.this.stdin;
      }

      public InputStream getInputStream() {
        return KubePodProcess2.this.stdout;
      }

      public InputStream getErrorStream() {
        return KubePodProcess2.this.stderr;
      }

      public int waitFor() throws InterruptedException {
        return KubePodProcess2.this.waitFor();
      }

      public int exitValue() {
        return KubePodProcess2.this.exitValue();
      }

      public void destroy() {
        KubePodProcess2.this.destroy();
      }

      public ProcessHandle.Info info() {
        return new KubePodProcessInfo(KubePodProcess2.this.podDefinition.getMetadata().getName());
      }
    };
  }

  public static ResourceRequirementsBuilder getResourceRequirementsBuilder(ResourceRequirements resourceRequirements) {
    if (resourceRequirements != null) {
      Map<String, Quantity> requestMap = new HashMap();
      if (!Strings.isNullOrEmpty(resourceRequirements.getCpuRequest())) {
        requestMap.put("cpu", Quantity.parse(resourceRequirements.getCpuRequest()));
      }

      if (!Strings.isNullOrEmpty(resourceRequirements.getMemoryRequest())) {
        requestMap.put("memory", Quantity.parse(resourceRequirements.getMemoryRequest()));
      }

      Map<String, Quantity> limitMap = new HashMap();
      if (!Strings.isNullOrEmpty(resourceRequirements.getCpuLimit())) {
        limitMap.put("cpu", Quantity.parse(resourceRequirements.getCpuLimit()));
      }

      if (!Strings.isNullOrEmpty(resourceRequirements.getMemoryLimit())) {
        limitMap.put("memory", Quantity.parse(resourceRequirements.getMemoryLimit()));
      }

      return (ResourceRequirementsBuilder)((ResourceRequirementsBuilder)(new ResourceRequirementsBuilder()).withRequests(requestMap)).withLimits(limitMap);
    } else {
      return new ResourceRequirementsBuilder();
    }
  }

  private static String prependPodInfo(String message, String podNamespace, String podName) {
    return String.format("(pod: %s / %s) - %s", podNamespace, podName, message);
  }

  static {
    DEFAULT_SIDECAR_RESOURCES = (new ResourceRequirements()).withMemoryLimit(configs.getSidecarKubeMemoryLimit()).withMemoryRequest(configs.getSidecarMemoryRequest()).withCpuLimit(configs.getSidecarKubeCpuLimit()).withCpuRequest(configs.getSidecarKubeCpuRequest());
    DEFAULT_SOCAT_RESOURCES = (new ResourceRequirements()).withMemoryLimit(configs.getSidecarKubeMemoryLimit()).withMemoryRequest(configs.getSidecarMemoryRequest()).withCpuLimit(configs.getSocatSidecarKubeCpuLimit()).withCpuRequest(configs.getSocatSidecarKubeCpuRequest());
    FAST_STDOUT_RESOURCES = (new ResourceRequirements()).withMemoryLimit("50Mi").withMemoryRequest("25Mi").withCpuLimit("2").withCpuRequest("1");
    INIT_RETRY_TIMEOUT_MINUTES = Duration.ofMinutes(5L);
    INIT_RETRY_MAX_ITERATIONS = (int)((double)INIT_RETRY_TIMEOUT_MINUTES.toSeconds() / 0.1);
  }
}
