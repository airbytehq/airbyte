/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.ContainerPort;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.EnvVar;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.SecretVolumeSourceBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.micronaut.core.util.StringUtils;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

/**
 * This process allows creating and managing a pod outside the lifecycle of the launching
 * application. Unlike {@link KubePodProcess} there is no heartbeat mechanism that requires the
 * launching pod and the launched pod to co-exist for the duration of execution for the launched
 * pod.
 * <p>
 * Instead, this process creates the pod and interacts with a document store on cloud storage to
 * understand the state of the created pod.
 * <p>
 * The document store is considered to be the truth when retrieving the status for an async pod
 * process. If the store isn't updated by the underlying pod, it will appear as failed.
 */
@Slf4j
public class AsyncOrchestratorPodProcess implements KubePod {

  public static final String KUBE_POD_INFO = "KUBE_POD_INFO";
  public static final String NO_OP = "NO_OP";

  private final KubePodInfo kubePodInfo;
  private final DocumentStoreClient documentStoreClient;
  private final KubernetesClient kubernetesClient;
  private final String secretName;
  private final String secretMountPath;
  private final String googleApplicationCredentials;
  private final String dataPlaneCredsSecretName;
  private final String dataPlaneCredsSecretMountPath;
  private final AtomicReference<Optional<Integer>> cachedExitValue;
  private final Map<String, String> environmentVariables;
  private final Integer serverPort;

  public AsyncOrchestratorPodProcess(
                                     final KubePodInfo kubePodInfo,
                                     final DocumentStoreClient documentStoreClient,
                                     final KubernetesClient kubernetesClient,
                                     final String secretName,
                                     final String secretMountPath,
                                     final String dataPlaneCredsSecretName,
                                     final String dataPlaneCredsSecretMountPath,
                                     final String googleApplicationCredentials,
                                     final Map<String, String> environmentVariables,
                                     final Integer serverPort) {
    this.kubePodInfo = kubePodInfo;
    this.documentStoreClient = documentStoreClient;
    this.kubernetesClient = kubernetesClient;
    this.secretName = secretName;
    this.secretMountPath = secretMountPath;
    this.dataPlaneCredsSecretName = dataPlaneCredsSecretName;
    this.dataPlaneCredsSecretMountPath = dataPlaneCredsSecretMountPath;
    this.googleApplicationCredentials = googleApplicationCredentials;
    this.cachedExitValue = new AtomicReference<>(Optional.empty());
    this.environmentVariables = environmentVariables;
    this.serverPort = serverPort;
  }

  public Optional<String> getOutput() {
    final var possibleOutput = getDocument(AsyncKubePodStatus.SUCCEEDED.name());

    if (possibleOutput.isPresent() && possibleOutput.get().isBlank()) {
      return Optional.empty();
    } else {
      return possibleOutput;
    }
  }

  private int computeExitValue() {
    final AsyncKubePodStatus docStoreStatus = getDocStoreStatus();

    // trust the doc store if it's in a terminal state
    if (docStoreStatus.equals(AsyncKubePodStatus.FAILED)) {
      log.warn("State Store reports orchestrator pod {} failed", getInfo().name());
      return 1;
    } else if (docStoreStatus.equals(AsyncKubePodStatus.SUCCEEDED)) {
      log.info("State Store reports orchestrator pod {} succeeded", getInfo().name());
      return 0;
    }

    final Pod pod = kubernetesClient.pods()
        .inNamespace(getInfo().namespace())
        .withName(getInfo().name())
        .get();

    // Since the pod creation blocks until the pod is created the first time,
    // if the pod no longer exists (and we don't have a success/fail document)
    // we must be in a failure state. If it wasn't able to write out its status
    // we must assume failure, since the document store is the "truth" for
    // async pod status.
    if (pod == null) {
      log.info("State Store missing status. Orchestrator pod {} non-existent. Assume failure.", getInfo().name());
      return 1;
    }

    // If the pod does exist, it may be in a terminal (error or completed) state.
    final boolean isTerminal = KubePodResourceHelper.isTerminal(pod);

    if (isTerminal) {
      // In case the doc store was updated in between when we pulled it and when
      // we read the status from the Kubernetes API, we need to check the doc store again.
      final AsyncKubePodStatus secondDocStoreStatus = getDocStoreStatus();
      if (secondDocStoreStatus.equals(AsyncKubePodStatus.FAILED)) {
        log.warn("State Store reports orchestrator pod {} failed", getInfo().name());
        return 1;
      } else if (secondDocStoreStatus.equals(AsyncKubePodStatus.SUCCEEDED)) {
        log.info("State Store reports orchestrator pod {} succeeded", getInfo().name());
        return 0;
      } else {
        // otherwise, the actual pod is terminal when the doc store says it shouldn't be.
        log.info("The current non terminal state is {}", secondDocStoreStatus);
        log.warn("State Store missing status, however orchestrator pod {} in terminal. Assume failure.", getInfo().name());
        return 1;
      }
    }

    // Otherwise, throw an exception because this is still running, which will be caught in hasExited
    switch (docStoreStatus) {
      case NOT_STARTED -> throw new IllegalThreadStateException("Pod hasn't started yet.");
      case INITIALIZING -> throw new IllegalThreadStateException("Pod is initializing.");
      default -> throw new IllegalThreadStateException("Pod is running.");
    }
  }

  @Override
  public int exitValue() {
    final var optionalCached = cachedExitValue.get();

    if (optionalCached.isPresent()) {
      return optionalCached.get();
    } else {
      final var exitValue = computeExitValue();
      cachedExitValue.set(Optional.of(exitValue));
      return exitValue;
    }
  }

  @Override
  public void destroy() {
    final var wasDestroyed = kubernetesClient.pods()
        .inNamespace(getInfo().namespace())
        .withName(getInfo().name())
        .withPropagationPolicy(DeletionPropagation.FOREGROUND)
        .delete();

    if (wasDestroyed) {
      log.info("Deleted pod {} in namespace {}", getInfo().name(), getInfo().namespace());
    } else {
      log.warn("Wasn't able to delete pod {} from namespace {}", getInfo().name(), getInfo().namespace());
    }
  }

  // implementation copied from Process.java since this isn't a real Process
  public boolean hasExited() {
    try {
      exitValue();
      return true;
    } catch (final IllegalThreadStateException e) {
      return false;
    }
  }

  public boolean waitFor(final long timeout, final TimeUnit unit) throws InterruptedException {
    // implementation copied from Process.java since this isn't a real Process
    long remainingNanos = unit.toNanos(timeout);
    if (hasExited()) {
      return true;
    }
    if (timeout <= 0) {
      return false;
    }

    final long deadline = System.nanoTime() + remainingNanos;
    do {
      // The remainingNanos bit is about calculating how much time left for the actual timeout.
      // Most of the time we should be sleeping for 500ms except when we get to the actual timeout.
      // We are waiting polling every 500ms for status. The trade-off here is between how often
      // we poll our status storage (GCS) and how reactive we are to detect that a process is done.
      Thread.sleep(Math.min(TimeUnit.NANOSECONDS.toMillis(remainingNanos) + 1, 500));
      if (hasExited()) {
        return true;
      }
      remainingNanos = deadline - System.nanoTime();
    } while (remainingNanos > 0);

    return false;
  }

  @Override
  public int waitFor() throws InterruptedException {
    final boolean exited = waitFor(10, TimeUnit.DAYS);

    if (exited) {
      return exitValue();
    } else {
      throw new InterruptedException("Pod did not complete within timeout.");
    }
  }

  @Override
  public KubePodInfo getInfo() {
    return kubePodInfo;
  }

  @Override
  public Process toProcess() {
    return new Process() {

      @Override
      public OutputStream getOutputStream() {
        try {
          final String output = AsyncOrchestratorPodProcess.this.getOutput().orElse("");
          final OutputStream os = new BufferedOutputStream(new ByteArrayOutputStream());
          os.write(output.getBytes(Charset.defaultCharset()));
          return os;
        } catch (final Exception e) {
          log.warn("Unable to write output to stream.", e);
          return OutputStream.nullOutputStream();
        }
      }

      @Override
      public InputStream getInputStream() {
        return InputStream.nullInputStream();
      }

      @Override
      public InputStream getErrorStream() {
        return InputStream.nullInputStream();
      }

      @Override
      public int waitFor() throws InterruptedException {
        return AsyncOrchestratorPodProcess.this.waitFor();
      }

      @Override
      public int exitValue() {
        return AsyncOrchestratorPodProcess.this.exitValue();
      }

      @Override
      public void destroy() {
        AsyncOrchestratorPodProcess.this.destroy();
      }

      @Override
      public boolean waitFor(final long timeout, final TimeUnit unit) throws InterruptedException {
        return AsyncOrchestratorPodProcess.this.waitFor(timeout, unit);
      }

    };
  }

  private Optional<String> getDocument(final String key) {
    return documentStoreClient.read(getInfo().namespace() + "/" + getInfo().name() + "/" + key);
  }

  private boolean checkStatus(final AsyncKubePodStatus status) {
    return getDocument(status.name()).isPresent();
  }

  /**
   * Checks terminal states first, then running, then initialized. Defaults to not started.
   * <p>
   * The order matters here!
   */
  public AsyncKubePodStatus getDocStoreStatus() {
    if (checkStatus(AsyncKubePodStatus.FAILED)) {
      return AsyncKubePodStatus.FAILED;
    } else if (checkStatus(AsyncKubePodStatus.SUCCEEDED)) {
      return AsyncKubePodStatus.SUCCEEDED;
    } else if (checkStatus(AsyncKubePodStatus.RUNNING)) {
      return AsyncKubePodStatus.RUNNING;
    } else if (checkStatus(AsyncKubePodStatus.INITIALIZING)) {
      return AsyncKubePodStatus.INITIALIZING;
    } else {
      return AsyncKubePodStatus.NOT_STARTED;
    }
  }

  // but does that mean there won't be a docker equivalent?
  public void create(final Map<String, String> allLabels,
                     final ResourceRequirements resourceRequirements,
                     final Map<String, String> fileMap,
                     final Map<Integer, Integer> portMap,
                     final Map<String, String> nodeSelectors) {
    final List<Volume> volumes = new ArrayList<>();
    final List<VolumeMount> volumeMounts = new ArrayList<>();
    final List<EnvVar> envVars = new ArrayList<>();

    volumes.add(new VolumeBuilder()
        .withName("airbyte-config")
        .withNewEmptyDir()
        .withMedium("Memory")
        .endEmptyDir()
        .build());

    volumeMounts.add(new VolumeMountBuilder()
        .withName("airbyte-config")
        .withMountPath(KubePodProcess.CONFIG_DIR)
        .build());

    if (secretName != null && secretMountPath != null && StringUtils.isNotEmpty(googleApplicationCredentials)) {
      volumes.add(new VolumeBuilder()
          .withName("airbyte-secret")
          .withSecret(new SecretVolumeSourceBuilder()
              .withSecretName(secretName)
              .withDefaultMode(420)
              .build())
          .build());

      volumeMounts.add(new VolumeMountBuilder()
          .withName("airbyte-secret")
          .withMountPath(secretMountPath)
          .build());

      envVars.add(new EnvVar(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, googleApplicationCredentials, null));

    }

    if (StringUtils.isNotEmpty(dataPlaneCredsSecretName) && StringUtils.isNotEmpty(dataPlaneCredsSecretMountPath)) {
      volumes.add(new VolumeBuilder()
          .withName("airbyte-dataplane-creds")
          .withSecret(new SecretVolumeSourceBuilder()
              .withSecretName(dataPlaneCredsSecretName)
              .withDefaultMode(420)
              .build())
          .build());

      volumeMounts.add(new VolumeMountBuilder()
          .withName("airbyte-dataplane-creds")
          .withMountPath(dataPlaneCredsSecretMountPath)
          .build());
    }

    // Copy all additionally provided environment variables
    envVars.addAll(environmentVariables.entrySet().stream().map(e -> new EnvVar(e.getKey(), e.getValue(), null)).toList());

    final List<ContainerPort> containerPorts = KubePodProcess.createContainerPortList(portMap);
    containerPorts.add(new ContainerPort(serverPort, null, null, null, null));

    final var initContainer = new ContainerBuilder()
        .withName(KubePodProcess.INIT_CONTAINER_NAME)
        .withImage("busybox:1.35")
        .withVolumeMounts(volumeMounts)
        .withCommand(List.of(
            "sh",
            "-c",
            String.format("""
                          i=0
                          until [ $i -gt 60 ]
                          do
                            echo "$i - waiting for config file transfer to complete..."
                            # check if the upload-complete file exists, if so exit without error
                            if [ -f "%s/%s" ]; then
                              exit 0
                            fi
                            i=$((i+1))
                            sleep 1
                          done
                          echo "config files did not transfer in time"
                          # no upload-complete file was created in time, exit with error
                          exit 1
                          """,
                KubePodProcess.CONFIG_DIR,
                KubePodProcess.SUCCESS_FILE_NAME)))
        .build();

    final var mainContainer = new ContainerBuilder()
        .withName(KubePodProcess.MAIN_CONTAINER_NAME)
        .withImage(kubePodInfo.mainContainerInfo().image())
        .withImagePullPolicy(kubePodInfo.mainContainerInfo().pullPolicy())
        .withResources(KubePodProcess.getResourceRequirementsBuilder(resourceRequirements).build())
        .withEnv(envVars)
        .withPorts(containerPorts)
        .withVolumeMounts(volumeMounts)
        .build();

    final Pod podToCreate = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName(getInfo().name())
        .withNamespace(getInfo().namespace())
        .withLabels(allLabels)
        .endMetadata()
        .withNewSpec()
        .withServiceAccount("airbyte-admin")
        .withAutomountServiceAccountToken(true)
        .withRestartPolicy("Never")
        .withContainers(mainContainer)
        .withInitContainers(initContainer)
        .withVolumes(volumes)
        .withNodeSelector(nodeSelectors)
        .endSpec()
        .build();

    // should only create after the kubernetes API creates the pod
    final var createdPod = kubernetesClient.pods()
        .inNamespace(getInfo().namespace())
        .createOrReplace(podToCreate);

    log.info("Waiting for pod to be running...");
    kubernetesClient.pods()
        .inNamespace(kubePodInfo.namespace())
        .withName(kubePodInfo.name())
        .waitUntilCondition(p -> !p.getStatus().getInitContainerStatuses().isEmpty()
            && p.getStatus().getInitContainerStatuses().get(0).getState().getWaiting() == null,
            5, TimeUnit.MINUTES);

    final var podStatus = kubernetesClient.pods()
        .inNamespace(kubePodInfo.namespace())
        .withName(kubePodInfo.name())
        .get()
        .getStatus();

    final var containerState = podStatus
        .getInitContainerStatuses()
        .get(0)
        .getState();

    if (containerState.getRunning() == null) {
      throw new RuntimeException("Pod was not running, state was: " + containerState);
    }

    log.info(String.format("Pod %s/%s is running on %s", kubePodInfo.namespace(), kubePodInfo.name(), podStatus.getPodIP()));

    final var updatedFileMap = new HashMap<>(fileMap);
    updatedFileMap.put(KUBE_POD_INFO, Jsons.serialize(kubePodInfo));

    copyFilesToKubeConfigVolumeMain(createdPod, updatedFileMap);
  }

  private static void copyFilesToKubeConfigVolumeMain(final Pod podDefinition, final Map<String, String> files) {
    final List<Map.Entry<String, String>> fileEntries = new ArrayList<>(files.entrySet());

    // copy this file last to indicate that the copy has completed
    fileEntries.add(new AbstractMap.SimpleEntry<>(KubePodProcess.SUCCESS_FILE_NAME, ""));

    Path tmpFile = null;
    Process proc = null;
    for (final Map.Entry<String, String> file : fileEntries) {
      try {
        tmpFile = Path.of(IOs.writeFileToRandomTmpDir(file.getKey(), file.getValue()));

        log.info("Uploading file: " + file.getKey());
        final var containerPath = Path.of(KubePodProcess.CONFIG_DIR + "/" + file.getKey());

        // using kubectl cp directly here, because both fabric and the official kube client APIs have
        // several issues with copying files. See https://github.com/airbytehq/airbyte/issues/8643 for
        // details.
        final String command = String.format("kubectl cp %s %s/%s:%s -c %s", tmpFile, podDefinition.getMetadata().getNamespace(),
            podDefinition.getMetadata().getName(), containerPath, KubePodProcess.INIT_CONTAINER_NAME);
        log.info(command);

        proc = Runtime.getRuntime().exec(command);
        log.info("Waiting for kubectl cp to complete");
        final int exitCode = proc.waitFor();

        if (exitCode != 0) {
          throw new IOException("kubectl cp failed with exit code " + exitCode);
        }

        log.info("kubectl cp complete, closing process");
      } catch (final IOException | InterruptedException e) {
        throw new RuntimeException(e);
      } finally {
        if (tmpFile != null) {
          tmpFile.toFile().delete();
        }
        if (proc != null) {
          proc.destroy();
        }
      }
    }
  }

}
