/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessFactory implements ProcessFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessFactory.class);

  public static final String JOB_TYPE = "job_type";
  public static final String SYNC_JOB = "sync";
  public static final String SPEC_JOB = "spec";
  public static final String CHECK_JOB = "check";
  public static final String DISCOVER_JOB = "discover";

  public static final String SYNC_RUNNER = "sync-runner";

  public static final String SYNC_STEP = "sync_step";
  public static final String READ_STEP = "read";
  public static final String WRITE_STEP = "write";
  public static final String NORMALISE_STEP = "normalise";
  public static final String CUSTOM_STEP = "custom";

  private static final Pattern ALPHABETIC = Pattern.compile("[a-zA-Z]+");;
  private static final String JOB_LABEL_KEY = "job_id";
  private static final String ATTEMPT_LABEL_KEY = "attempt_id";
  private static final String WORKER_POD_LABEL_KEY = "airbyte";
  private static final String WORKER_POD_LABEL_VALUE = "worker-pod";

  private final WorkerConfigs workerConfigs;
  private final String namespace;
  private final KubernetesClient fabricClient;
  private final String kubeHeartbeatUrl;
  private final String processRunnerHost;
  private final boolean isOrchestrator;
  private final Duration statusCheckInterval;

  /**
   * Sets up a process factory with the default processRunnerHost.
   */
  public KubeProcessFactory(final WorkerConfigs workerConfigs,
                            final String namespace,
                            final KubernetesClient fabricClient,
                            final String kubeHeartbeatUrl,
                            final boolean isOrchestrator) {
    this(workerConfigs, namespace, fabricClient, kubeHeartbeatUrl,
        Exceptions.toRuntime(() -> InetAddress.getLocalHost().getHostAddress()), isOrchestrator, KubePodProcess.DEFAULT_STATUS_CHECK_INTERVAL);
  }

  /**
   * @param namespace kubernetes namespace where spawned pods will live
   * @param fabricClient fabric8 kubernetes client
   * @param kubeHeartbeatUrl a url where if the response is not 200 the spawned process will fail
   *        itself
   * @param processRunnerHost is the local host or ip of the machine running the process factory.
   *        injectable for testing.
   * @param isOrchestrator determines if this should run as airbyte-admin
   * @param statusCheckInterval specifies how often the Kubernetes API should be consulted when
   *        attempting to get the exit code after termination
   */
  @VisibleForTesting
  public KubeProcessFactory(final WorkerConfigs workerConfigs,
                            final String namespace,
                            final KubernetesClient fabricClient,
                            final String kubeHeartbeatUrl,
                            final String processRunnerHost,
                            final boolean isOrchestrator,
                            final Duration statusCheckInterval) {
    this.workerConfigs = workerConfigs;
    this.namespace = namespace;
    this.fabricClient = fabricClient;
    this.kubeHeartbeatUrl = kubeHeartbeatUrl;
    this.processRunnerHost = processRunnerHost;
    this.isOrchestrator = isOrchestrator;
    this.statusCheckInterval = statusCheckInterval;
  }

  @Override
  public Process create(final String jobId,
                        final int attempt,
                        final Path jobRoot, // todo: remove unused
                        final String imageName,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final ResourceRequirements resourceRequirements,
                        final Map<String, String> customLabels,
                        final Map<Integer, Integer> internalToExternalPorts,
                        final String... args)
      throws WorkerException {
    try {
      // used to differentiate source and destination processes with the same id and attempt
      final String podName = createPodName(imageName, jobId, attempt);
      LOGGER.info("Attempting to start pod = {}", podName);

      final int stdoutLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stdoutLocalPort = {}", podName, stdoutLocalPort);

      final int stderrLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stderrLocalPort = {}", podName, stderrLocalPort);

      final var allLabels = getLabels(jobId, attempt, customLabels);

      return new KubePodProcess(
          isOrchestrator,
          processRunnerHost,
          fabricClient,
          statusCheckInterval,
          podName,
          namespace,
          imageName,
          workerConfigs.getJobImagePullPolicy(),
          stdoutLocalPort,
          stderrLocalPort,
          kubeHeartbeatUrl,
          usesStdin,
          files,
          entrypoint,
          resourceRequirements,
          workerConfigs.getJobImagePullSecret(),
          workerConfigs.getWorkerKubeTolerations(),
          workerConfigs.getworkerKubeNodeSelectors(),
          allLabels,
          workerConfigs.getJobSocatImage(),
          workerConfigs.getJobBusyboxImage(),
          workerConfigs.getJobCurlImage(),
          workerConfigs.getEnvMap(),
          internalToExternalPorts,
          args);
    } catch (final Exception e) {
      throw new WorkerException(e.getMessage(), e);
    }
  }

  public static Map<String, String> getLabels(final String jobId, final int attemptId, final Map<String, String> customLabels) {
    final var allLabels = new HashMap<>(customLabels);

    final var generalKubeLabels = Map.of(
        JOB_LABEL_KEY, jobId,
        ATTEMPT_LABEL_KEY, String.valueOf(attemptId),
        WORKER_POD_LABEL_KEY, WORKER_POD_LABEL_VALUE);

    allLabels.putAll(generalKubeLabels);

    return allLabels;
  }

  /**
   * Docker image names are by convention separated by slashes. The last portion is the image's name.
   * This is followed by a colon and a version number. e.g. airbyte/scheduler:v1 or
   * gcr.io/my-project/image-name:v2.
   *
   * Kubernetes has a maximum pod name length of 63 characters, and names must start with an
   * alphabetic character.
   *
   * With these two facts, attempt to construct a unique Pod name with the image name present for
   * easier operations.
   */
  @VisibleForTesting
  protected static String createPodName(final String fullImagePath, final String jobId, final int attempt) {
    final var versionDelimiter = ":";
    final var noVersion = fullImagePath.split(versionDelimiter)[0];

    final var dockerDelimiter = "/";
    final var nameParts = noVersion.split(dockerDelimiter);
    var imageName = nameParts[nameParts.length - 1];

    final var randSuffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String suffix = "sync" + "-" + jobId + "-" + attempt + "-" + randSuffix;

    var podName = imageName + "-" + suffix;
    final var podNameLenLimit = 63;
    if (podName.length() > podNameLenLimit) {
      final var extra = podName.length() - podNameLenLimit;
      imageName = imageName.substring(extra);
      podName = imageName + "-" + suffix;
    }
    final Matcher m = ALPHABETIC.matcher(podName);
    // Since we add sync-UUID as a suffix a couple of lines up, there will always be a substring
    // starting with an alphabetic character.
    // If the image name is a no-op, this function should always return `sync-UUID` at the minimum.
    m.find();
    return podName.substring(m.start());
  }

}
