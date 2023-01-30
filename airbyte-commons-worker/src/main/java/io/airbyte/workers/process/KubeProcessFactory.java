/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessFactory implements ProcessFactory {

  @VisibleForTesting
  public static final int KUBE_NAME_LEN_LIMIT = 63;

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessFactory.class);

  private final WorkerConfigs workerConfigs;
  private final String namespace;
  private final KubernetesClient fabricClient;
  private final String kubeHeartbeatUrl;
  private final String processRunnerHost;
  private final boolean isOrchestrator;

  /**
   * Sets up a process factory with the default processRunnerHost.
   */
  public KubeProcessFactory(final WorkerConfigs workerConfigs,
                            final String namespace,
                            final KubernetesClient fabricClient,
                            final String kubeHeartbeatUrl,
                            final boolean isOrchestrator) {
    this(
        workerConfigs,
        namespace,
        fabricClient,
        kubeHeartbeatUrl,
        Exceptions.toRuntime(() -> InetAddress.getLocalHost().getHostAddress()),
        isOrchestrator);
  }

  /**
   * @param namespace kubernetes namespace where spawned pods will live
   * @param fabricClient fabric8 kubernetes client
   * @param kubeHeartbeatUrl a url where if the response is not 200 the spawned process will fail
   *        itself
   * @param processRunnerHost is the local host or ip of the machine running the process factory.
   *        injectable for testing.
   * @param isOrchestrator determines if this should run as airbyte-admin
   */
  @VisibleForTesting
  public KubeProcessFactory(final WorkerConfigs workerConfigs,
                            final String namespace,
                            final KubernetesClient fabricClient,
                            final String kubeHeartbeatUrl,
                            final String processRunnerHost,
                            final boolean isOrchestrator) {
    this.workerConfigs = workerConfigs;
    this.namespace = namespace;
    this.fabricClient = fabricClient;
    this.kubeHeartbeatUrl = kubeHeartbeatUrl;
    this.processRunnerHost = processRunnerHost;
    this.isOrchestrator = isOrchestrator;
  }

  @Override
  public Process create(
                        final String jobType,
                        final String jobId,
                        final int attempt,
                        final Path jobRoot,
                        final String imageName,
                        final boolean isCustomConnector,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final ResourceRequirements resourceRequirements,
                        final AllowedHosts allowedHosts,
                        final Map<String, String> customLabels,
                        final Map<String, String> jobMetadata,
                        final Map<Integer, Integer> internalToExternalPorts,
                        final String... args)
      throws WorkerException {
    try {
      // used to differentiate source and destination processes with the same id and attempt
      final String podName = ProcessFactory.createProcessName(imageName, jobType, jobId, attempt, KUBE_NAME_LEN_LIMIT);
      LOGGER.info("Attempting to start pod = {} for {} with resources {} and allowedHosts {}", podName, imageName, resourceRequirements,
          allowedHosts);

      final int stdoutLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stdoutLocalPort = {}", podName, stdoutLocalPort);

      final int stderrLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stderrLocalPort = {}", podName, stderrLocalPort);

      final var allLabels = getLabels(jobId, attempt, customLabels);

      // If using isolated pool, check workerConfigs has isolated pool set. If not set, fall back to use
      // regular node pool.
      final var nodeSelectors =
          isCustomConnector ? workerConfigs.getWorkerIsolatedKubeNodeSelectors().orElse(workerConfigs.getworkerKubeNodeSelectors())
              : workerConfigs.getworkerKubeNodeSelectors();

      return new KubePodProcess(
          isOrchestrator,
          processRunnerHost,
          fabricClient,
          podName,
          namespace,
          imageName,
          workerConfigs.getJobImagePullPolicy(),
          workerConfigs.getSidecarImagePullPolicy(),
          stdoutLocalPort,
          stderrLocalPort,
          kubeHeartbeatUrl,
          usesStdin,
          files,
          entrypoint,
          resourceRequirements,
          workerConfigs.getJobImagePullSecrets(),
          workerConfigs.getWorkerKubeTolerations(),
          nodeSelectors,
          allLabels,
          workerConfigs.getWorkerKubeAnnotations(),
          workerConfigs.getJobSocatImage(),
          workerConfigs.getJobBusyboxImage(),
          workerConfigs.getJobCurlImage(),
          MoreMaps.merge(jobMetadata, workerConfigs.getEnvMap()),
          internalToExternalPorts,
          args).toProcess();
    } catch (final Exception e) {
      throw new WorkerException(e.getMessage(), e);
    }
  }

  /**
   * Returns general labels to be applied to all Kubernetes pods. All general labels should be added
   * here.
   */
  public static Map<String, String> getLabels(final String jobId, final int attemptId, final Map<String, String> customLabels) {
    final var allLabels = new HashMap<>(customLabels);

    final var generalKubeLabels = Map.of(
        Metadata.JOB_LABEL_KEY, jobId,
        Metadata.ATTEMPT_LABEL_KEY, String.valueOf(attemptId),
        Metadata.WORKER_POD_LABEL_KEY, Metadata.WORKER_POD_LABEL_VALUE);

    allLabels.putAll(generalKubeLabels);

    return allLabels;
  }

}
