/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.ContainerPort;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
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
 *
 * Instead, this process creates the pod and interacts with a document store on cloud storage to
 * understand the state of the created pod.
 */
@Slf4j
public class AsyncOrchestratorPodProcess implements KubePod {

  public static final String KUBE_POD_INFO = "KUBE_POD_INFO";
  public static final String NO_OP = "NO_OP";

  private final KubePodInfo kubePodInfo;
  private final DocumentStoreClient documentStoreClient;
  private final KubernetesClient kubernetesClient;
  private final AtomicReference<Optional<Integer>> cachedExitValue;

  public AsyncOrchestratorPodProcess(
                                     final KubePodInfo kubePodInfo,
                                     final DocumentStoreClient documentStoreClient,
                                     final KubernetesClient kubernetesClient) {
    this.kubePodInfo = kubePodInfo;
    this.documentStoreClient = documentStoreClient;
    this.kubernetesClient = kubernetesClient;
    this.cachedExitValue = new AtomicReference<>(Optional.empty());
  }

  public Optional<String> getOutput() {
    return getDocument(AsyncKubePodStatus.SUCCEEDED.name());
  }

  private int computeExitValue() {
    final AsyncKubePodStatus docStoreStatus = getDocStoreStatus();

    // trust the doc store if it's in a terminal state
    if (docStoreStatus.equals(AsyncKubePodStatus.FAILED)) {
      return 1;
    } else if (docStoreStatus.equals(AsyncKubePodStatus.SUCCEEDED)) {
      return 0;
    }

    final Pod pod = kubernetesClient.pods()
        .inNamespace(getInfo().namespace())
        .withName(getInfo().name())
        .get();

    // Since the pod creation blocks until the pod is created the first time,
    // if the pod no longer exists (and we don't have a success/fail document)
    // we must be in a state where it completed and therefore failed
    if (pod == null) {
      return 1;
    }

    // If the pod does exist, it may be in a terminal (error or completed) state.
    final boolean isTerminal = KubePodProcess.isTerminal(pod);

    if (isTerminal) {
      // In case the doc store was updated in between when we pulled it and when
      // we read the status from the Kubernetes API, we need to check the doc store again.
      final AsyncKubePodStatus secondDocStoreStatus = getDocStoreStatus();
      if (secondDocStoreStatus.equals(AsyncKubePodStatus.FAILED)) {
        return 1;
      } else if (secondDocStoreStatus.equals(AsyncKubePodStatus.SUCCEEDED)) {
        return 0;
      } else {
        // otherwise, the actual pod is terminal when the doc store says it shouldn't be.
        return 1;
      }
    }

    // Otherwise, throw an exception because this is still running.
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
    } catch (IllegalThreadStateException e) {
      return false;
    }
  }

  @Override
  public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
    // implementation copied from Process.java since this isn't a real Process
    long remainingNanos = unit.toNanos(timeout);
    if (hasExited())
      return true;
    if (timeout <= 0)
      return false;

    long deadline = System.nanoTime() + remainingNanos;
    do {
      // todo: allow scaling this value to not ddos the api, just like KubePodProcess
      Thread.sleep(Math.min(TimeUnit.NANOSECONDS.toMillis(remainingNanos) + 1, 100));
      if (hasExited())
        return true;
      remainingNanos = deadline - System.nanoTime();
    } while (remainingNanos > 0);

    return false;
  }

  @Override
  public int waitFor() throws InterruptedException {
    boolean exited = waitFor(10, TimeUnit.DAYS);

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

  private Optional<String> getDocument(final String key) {
    return documentStoreClient.read(getInfo().namespace() + "/" + getInfo().name() + "/" + key);
  }

  private boolean checkStatus(final AsyncKubePodStatus status) {
    return getDocument(status.name()).isPresent();
  }

  public AsyncKubePodStatus getDocStoreStatus() {
    if (checkStatus(AsyncKubePodStatus.INITIALIZING)) {
      return AsyncKubePodStatus.INITIALIZING;
    } else if (checkStatus(AsyncKubePodStatus.RUNNING)) {
      return AsyncKubePodStatus.RUNNING;
    } else if (checkStatus(AsyncKubePodStatus.FAILED)) {
      return AsyncKubePodStatus.FAILED;
    } else if (checkStatus(AsyncKubePodStatus.SUCCEEDED)) {
      return AsyncKubePodStatus.SUCCEEDED;
    } else {
      return AsyncKubePodStatus.NOT_STARTED;
    }
  }

  // but does that mean there won't be a docker equivalent?
  public void create(final String airbyteVersion,
                     final Map<String, String> allLabels,
                     final ResourceRequirements resourceRequirements,
                     final Map<String, String> fileMap,
                     final Map<Integer, Integer> portMap) {
    final Volume configVolume = new VolumeBuilder()
        .withName("airbyte-config")
        .withNewEmptyDir()
        .withMedium("Memory")
        .endEmptyDir()
        .build();

    final VolumeMount configVolumeMount = new VolumeMountBuilder()
        .withName("airbyte-config")
        .withMountPath(KubePodProcess.CONFIG_DIR)
        .build();

    final List<ContainerPort> containerPorts = KubePodProcess.createContainerPortList(portMap);

    final var mainContainer = new ContainerBuilder()
        .withName("main")
        .withImage("airbyte/container-orchestrator:" + airbyteVersion)
        .withResources(KubePodProcess.getResourceRequirementsBuilder(resourceRequirements).build())
        .withPorts(containerPorts)
        .withPorts(new ContainerPort(WorkerApp.KUBE_HEARTBEAT_PORT, null, null, null, null))
        .withVolumeMounts(configVolumeMount)
        .build();

    final Pod pod = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName(getInfo().name())
        .withNamespace(getInfo().namespace())
        .withLabels(allLabels)
        .endMetadata()
        .withNewSpec()
        .withServiceAccount("airbyte-admin").withAutomountServiceAccountToken(true)
        .withRestartPolicy("Never")
        .withContainers(mainContainer)
        .withVolumes(configVolume)
        .endSpec()
        .build();

    // should only create after the kubernetes API creates the pod
    final var createdPod = kubernetesClient.pods().createOrReplace(pod);

    log.info("Waiting for pod to be running...");
    try {
      kubernetesClient.pods()
          .inNamespace(kubePodInfo.namespace())
          .withName(kubePodInfo.name())
          .waitUntilCondition(p -> {
            return !p.getStatus().getContainerStatuses().isEmpty() && p.getStatus().getContainerStatuses().get(0).getState().getWaiting() == null;
          }, 5, TimeUnit.MINUTES);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }

    final var containerState = kubernetesClient.pods()
        .inNamespace(kubePodInfo.namespace())
        .withName(kubePodInfo.name())
        .get()
        .getStatus()
        .getContainerStatuses()
        .get(0)
        .getState();

    if (containerState.getRunning() == null) {
      throw new RuntimeException("Pod was not running, state was: " + containerState);
    }

    final var updatedFileMap = new HashMap<>(fileMap);
    updatedFileMap.put(KUBE_POD_INFO, Jsons.serialize(kubePodInfo));

    KubePodProcess.copyFilesToKubeConfigVolumeMain(createdPod, updatedFileMap);
  }

}
