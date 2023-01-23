/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.PROCESS_EXIT_VALUE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;
import static io.airbyte.workers.process.Metadata.CONNECTION_ID_LABEL_KEY;
import static io.airbyte.workers.process.Metadata.ORCHESTRATOR_STEP;
import static io.airbyte.workers.process.Metadata.SYNC_STEP_KEY;

import com.google.common.base.Stopwatch;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.sync.OrchestratorConstants;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubeContainerInfo;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodResourceHelper;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.KubernetesClientException;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CancellationException;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * Coordinates configuring and managing the state of an async process. This is tied to the (job_id,
 * attempt_id) and will attempt to kill off lower attempt ids.
 *
 * @param <INPUT> a json-serializable input class for the worker
 * @param <OUTPUT> either {@link Void} or a json-serializable output class for the worker
 */
@Slf4j
public class LauncherWorker<INPUT, OUTPUT> implements Worker<INPUT, OUTPUT> {

  private static final Duration MAX_DELETION_TIMEOUT = Duration.ofSeconds(45);

  private final UUID connectionId;
  private final String application;
  private final String podNamePrefix;
  private final JobRunConfig jobRunConfig;
  private final Map<String, String> additionalFileMap;
  private final ContainerOrchestratorConfig containerOrchestratorConfig;
  private final ResourceRequirements resourceRequirements;
  private final Class<OUTPUT> outputClass;
  private final Supplier<ActivityExecutionContext> activityContext;
  private final Integer serverPort;
  private final TemporalUtils temporalUtils;
  private final WorkerConfigs workerConfigs;

  private final boolean isCustomConnector;
  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private AsyncOrchestratorPodProcess process;

  public LauncherWorker(final UUID connectionId,
                        final String application,
                        final String podNamePrefix,
                        final JobRunConfig jobRunConfig,
                        final Map<String, String> additionalFileMap,
                        final ContainerOrchestratorConfig containerOrchestratorConfig,
                        final ResourceRequirements resourceRequirements,
                        final Class<OUTPUT> outputClass,
                        final Supplier<ActivityExecutionContext> activityContext,
                        final Integer serverPort,
                        final TemporalUtils temporalUtils,
                        final WorkerConfigs workerConfigs,
                        final boolean isCustomConnector) {

    this.connectionId = connectionId;
    this.application = application;
    this.podNamePrefix = podNamePrefix;
    this.jobRunConfig = jobRunConfig;
    this.additionalFileMap = additionalFileMap;
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.resourceRequirements = resourceRequirements;
    this.outputClass = outputClass;
    this.activityContext = activityContext;
    this.serverPort = serverPort;
    this.temporalUtils = temporalUtils;
    this.workerConfigs = workerConfigs;
    this.isCustomConnector = isCustomConnector;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public OUTPUT run(final INPUT input, final Path jobRoot) throws WorkerException {
    final AtomicBoolean isCanceled = new AtomicBoolean(false);
    final AtomicReference<Runnable> cancellationCallback = new AtomicReference<>(null);
    return temporalUtils.withBackgroundHeartbeat(cancellationCallback, () -> {
      try {
        // Assemble configuration.
        final Map<String, String> envMap = System.getenv().entrySet().stream()
            .filter(entry -> OrchestratorConstants.ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

        // Manually add the worker environment to the env var map
        envMap.put(WorkerConstants.WORKER_ENVIRONMENT, containerOrchestratorConfig.workerEnvironment().name());

        final Map<String, String> fileMap = new HashMap<>(additionalFileMap);
        fileMap.putAll(Map.of(
            OrchestratorConstants.INIT_FILE_APPLICATION, application,
            OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
            OrchestratorConstants.INIT_FILE_INPUT, Jsons.serialize(input),
            OrchestratorConstants.INIT_FILE_ENV_MAP, Jsons.serialize(envMap)));

        final Map<Integer, Integer> portMap = Map.of(
            serverPort, serverPort,
            OrchestratorConstants.PORT1, OrchestratorConstants.PORT1,
            OrchestratorConstants.PORT2, OrchestratorConstants.PORT2,
            OrchestratorConstants.PORT3, OrchestratorConstants.PORT3,
            OrchestratorConstants.PORT4, OrchestratorConstants.PORT4);

        final var allLabels = KubeProcessFactory.getLabels(
            jobRunConfig.getJobId(),
            Math.toIntExact(jobRunConfig.getAttemptId()),
            Map.of(CONNECTION_ID_LABEL_KEY, connectionId.toString(), SYNC_STEP_KEY, ORCHESTRATOR_STEP));

        final var podNameAndJobPrefix = podNamePrefix + "-job-" + jobRunConfig.getJobId() + "-attempt-";
        final var podName = podNameAndJobPrefix + jobRunConfig.getAttemptId();
        final var mainContainerInfo = new KubeContainerInfo(containerOrchestratorConfig.containerOrchestratorImage(),
            containerOrchestratorConfig.containerOrchestratorImagePullPolicy());
        final var kubePodInfo = new KubePodInfo(containerOrchestratorConfig.namespace(),
            podName,
            mainContainerInfo);

        ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, connectionId, JOB_ID_KEY, jobRunConfig.getJobId(), JOB_ROOT_KEY, jobRoot));

        // Use the configuration to create the process.
        process = new AsyncOrchestratorPodProcess(
            kubePodInfo,
            containerOrchestratorConfig.documentStoreClient(),
            containerOrchestratorConfig.kubernetesClient(),
            containerOrchestratorConfig.secretName(),
            containerOrchestratorConfig.secretMountPath(),
            containerOrchestratorConfig.dataPlaneCredsSecretName(),
            containerOrchestratorConfig.dataPlaneCredsSecretMountPath(),
            containerOrchestratorConfig.googleApplicationCredentials(),
            containerOrchestratorConfig.environmentVariables(),
            serverPort);

        // Define what to do on cancellation.
        cancellationCallback.set(() -> {
          // When cancelled, try to set to true.
          // Only proceed if value was previously false, so we only have one cancellation going. at a time
          if (!isCanceled.getAndSet(true)) {
            log.info("Trying to cancel async pod process.");
            process.destroy();
          }
        });

        // only kill running pods and create process if it is not already running.
        if (process.getDocStoreStatus().equals(AsyncKubePodStatus.NOT_STARTED)) {
          log.info("Creating " + podName + " for attempt number: " + jobRunConfig.getAttemptId());
          killRunningPodsForConnection();

          // custom connectors run in an isolated node pool from airbyte-supported connectors
          // to reduce the blast radius of any problems with custom connector code.
          final var nodeSelectors =
              isCustomConnector ? workerConfigs.getWorkerIsolatedKubeNodeSelectors().orElse(workerConfigs.getworkerKubeNodeSelectors())
                  : workerConfigs.getworkerKubeNodeSelectors();

          try {
            process.create(
                allLabels,
                resourceRequirements,
                fileMap,
                portMap,
                nodeSelectors);
          } catch (final KubernetesClientException e) {
            ApmTraceUtils.addExceptionToTrace(e);
            throw new WorkerException(
                "Failed to create pod " + podName + ", pre-existing pod exists which didn't advance out of the NOT_STARTED state.", e);
          }
        }

        // this waitFor can resume if the activity is re-run
        process.waitFor();

        if (cancelled.get()) {
          final CancellationException e = new CancellationException();
          ApmTraceUtils.addExceptionToTrace(e);
          throw e;
        }

        final int asyncProcessExitValue = process.exitValue();
        if (asyncProcessExitValue != 0) {
          final WorkerException e = new WorkerException("Orchestrator process exited with non-zero exit code: " + asyncProcessExitValue);
          ApmTraceUtils.addTagsToTrace(Map.of(PROCESS_EXIT_VALUE_KEY, asyncProcessExitValue));
          ApmTraceUtils.addExceptionToTrace(e);
          throw e;
        }

        final var output = process.getOutput();

        return output.map(s -> Jsons.deserialize(s, outputClass)).orElse(null);
      } catch (final Exception e) {
        ApmTraceUtils.addExceptionToTrace(e);
        if (cancelled.get()) {
          try {
            log.info("Destroying process due to cancellation.");
            process.destroy();
          } catch (final Exception e2) {
            log.error("Failed to destroy process on cancellation.", e2);
          }
          throw new WorkerException("Launcher " + application + " was cancelled.", e);
        } else {
          throw new WorkerException("Running the launcher " + application + " failed", e);
        }
      }
    }, activityContext);
  }

  /**
   * It is imperative that we do not run multiple replications, normalizations, syncs, etc. at the
   * same time. Our best bet is to kill everything that is labelled with the connection id and wait
   * until no more pods exist with that connection id.
   */
  private void killRunningPodsForConnection() {
    final var client = containerOrchestratorConfig.kubernetesClient();

    // delete all pods with the connection id label
    List<Pod> runningPods = getNonTerminalPodsWithLabels();
    final Stopwatch stopwatch = Stopwatch.createStarted();

    while (!runningPods.isEmpty() && stopwatch.elapsed().compareTo(MAX_DELETION_TIMEOUT) < 0) {
      log.warn("There are currently running pods for the connection: {}. Killing these pods to enforce one execution at a time.",
          getPodNames(runningPods).toString());

      log.info("Attempting to delete pods: {}", getPodNames(runningPods).toString());
      runningPods.stream()
          .parallel()
          .forEach(kubePod -> client.resource(kubePod).withPropagationPolicy(DeletionPropagation.FOREGROUND).delete());

      log.info("Waiting for deletion...");
      Exceptions.toRuntime(() -> Thread.sleep(1000));

      runningPods = getNonTerminalPodsWithLabels();
    }

    if (runningPods.isEmpty()) {
      log.info("Successfully deleted all running pods for the connection!");
    } else {
      final RuntimeException e = new RuntimeException("Unable to delete pods: " + getPodNames(runningPods).toString());
      ApmTraceUtils.addExceptionToTrace(e);
      throw e;
    }
  }

  private List<String> getPodNames(final List<Pod> pods) {
    return pods.stream().map(pod -> pod.getMetadata().getName()).collect(Collectors.toList());
  }

  private List<Pod> getNonTerminalPodsWithLabels() {
    return containerOrchestratorConfig.kubernetesClient().pods()
        .inNamespace(containerOrchestratorConfig.namespace())
        .withLabels(Map.of(CONNECTION_ID_LABEL_KEY, connectionId.toString()))
        .list()
        .getItems()
        .stream()
        .filter(kubePod -> !KubePodResourceHelper.isTerminal(kubePod))
        .collect(Collectors.toList());
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() {
    cancelled.set(true);

    if (process == null) {
      return;
    }

    log.debug("Closing sync runner process");
    killRunningPodsForConnection();

    if (process.hasExited()) {
      log.info("Successfully cancelled process.");
    } else {
      // try again
      killRunningPodsForConnection();

      if (process.hasExited()) {
        log.info("Successfully cancelled process.");
      } else {
        log.error("Unable to cancel process");
      }
    }
  }

}
