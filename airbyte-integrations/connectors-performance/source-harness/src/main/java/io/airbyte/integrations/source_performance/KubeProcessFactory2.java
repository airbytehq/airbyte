package io.airbyte.integrations.source_performance;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.InetAddress;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public class KubeProcessFactory2 implements ProcessFactory {
  @VisibleForTesting
  public static final int KUBE_NAME_LEN_LIMIT = 63;
  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessFactory.class);
  private final WorkerConfigs workerConfigs;
  private final String namespace;
  private final KubernetesClient fabricClient;
  private final String kubeHeartbeatUrl;
  private final String processRunnerHost;
  private final boolean isOrchestrator;

  public KubeProcessFactory2(WorkerConfigs workerConfigs, String namespace, KubernetesClient fabricClient, String kubeHeartbeatUrl, boolean isOrchestrator) {
    this(workerConfigs, namespace, fabricClient, kubeHeartbeatUrl, (String) Exceptions.toRuntime(() -> {
      return InetAddress.getLocalHost().getHostAddress();
    }), isOrchestrator);
  }

  @VisibleForTesting
  public KubeProcessFactory2(WorkerConfigs workerConfigs, String namespace, KubernetesClient fabricClient, String kubeHeartbeatUrl, String processRunnerHost, boolean isOrchestrator) {
    this.workerConfigs = workerConfigs;
    this.namespace = namespace;
    this.fabricClient = fabricClient;
    this.kubeHeartbeatUrl = kubeHeartbeatUrl;
    this.processRunnerHost = processRunnerHost;
    this.isOrchestrator = isOrchestrator;
  }

  public Process create(String jobType, String jobId, int attempt, Path jobRoot, String imageName, boolean isCustomConnector, boolean usesStdin, Map<String, String> files, String entrypoint, ResourceRequirements resourceRequirements, AllowedHosts allowedHosts, Map<String, String> customLabels, Map<String, String> jobMetadata, Map<Integer, Integer> internalToExternalPorts, String... args) throws WorkerException {
    try {
      String podName = ProcessFactory.createProcessName(imageName, jobType, jobId, attempt, 63);
      LOGGER.info("Attempting to start pod = {} for {} with resources {} and allowedHosts {}", new Object[]{podName, imageName, resourceRequirements, allowedHosts});
      int stdoutLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stdoutLocalPort = {}", podName, stdoutLocalPort);
      int stderrLocalPort = KubePortManagerSingleton.getInstance().take();
      LOGGER.info("{} stderrLocalPort = {}", podName, stderrLocalPort);
      Map<String, String> allLabels = getLabels(jobId, attempt, customLabels);
      Map<String, String> nodeSelectors = isCustomConnector ? (Map)this.workerConfigs.getWorkerIsolatedKubeNodeSelectors().orElse(this.workerConfigs.getworkerKubeNodeSelectors()) : this.workerConfigs.getworkerKubeNodeSelectors();
      return (new KubePodProcess2(this.isOrchestrator, this.processRunnerHost, this.fabricClient, podName, this.namespace, imageName, this.workerConfigs.getJobImagePullPolicy(), this.workerConfigs.getSidecarImagePullPolicy(), stdoutLocalPort, stderrLocalPort, this.kubeHeartbeatUrl, usesStdin, files, entrypoint, resourceRequirements, this.workerConfigs.getJobImagePullSecrets(), this.workerConfigs.getWorkerKubeTolerations(), nodeSelectors, allLabels, this.workerConfigs.getWorkerKubeAnnotations(), this.workerConfigs.getJobSocatImage(), this.workerConfigs.getJobBusyboxImage(), this.workerConfigs.getJobCurlImage(), MoreMaps.merge(new Map[]{jobMetadata, this.workerConfigs.getEnvMap()}), internalToExternalPorts, args)).toProcess();
    } catch (Exception var21) {
      throw new WorkerException(var21.getMessage(), var21);
    }
  }

  public static Map<String, String> getLabels(String jobId, int attemptId, Map<String, String> customLabels) {
    HashMap<String, String> allLabels = new HashMap(customLabels);
    Map<String, String> generalKubeLabels = Map.of("job_id", jobId, "attempt_id", String.valueOf(attemptId), "airbyte", "job-pod");
    allLabels.putAll(generalKubeLabels);
    return allLabels;
  }
}
