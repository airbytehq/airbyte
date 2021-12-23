/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultReplicationWorker;
import io.airbyte.workers.ReplicationWorker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.protocols.airbyte.NamespacingMapper;
import io.airbyte.workers.temporal.sync.ReplicationLauncherWorker;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Entrypoint for the application responsible for launching containers and handling all message
 * passing. Currently, this is only implemented for replication but in the future it will be
 * available for normalization and dbt. Also, the current version relies on a heartbeat from a
 * Temporal worker. This will also be removed in the future so this can run fully async.
 *
 * This application retrieves most of its configuration from copied files from the calling Temporal
 * worker.
 *
 * This app uses default logging which is directly captured by the calling Temporal worker. In the
 * future this will need to independently interact with cloud storage.
 */
public class ContainerOrchestratorApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(ContainerOrchestratorApp.class);

  private static void replicationRunner(final Configs configs) throws IOException, WorkerException {

    LOGGER.info("Starting replication runner app...");

    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);
    final ProcessFactory processFactory = getProcessBuilderFactory(configs, workerConfigs);

    LOGGER.info("Attempting to retrieve config files...");

    final JobRunConfig jobRunConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_JOB_RUN_CONFIG)), JobRunConfig.class);

    final IntegrationLauncherConfig sourceLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_SOURCE_LAUNCHER_CONFIG)), IntegrationLauncherConfig.class);

    final IntegrationLauncherConfig destinationLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG)),
            IntegrationLauncherConfig.class);

    final StandardSyncInput syncInput =
        Jsons.deserialize(Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_SYNC_INPUT)), StandardSyncInput.class);

    LOGGER.info("Setting up source launcher...");
    final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
        sourceLauncherConfig.getJobId(),
        Math.toIntExact(sourceLauncherConfig.getAttemptId()),
        sourceLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getResourceRequirements());

    LOGGER.info("Setting up destination launcher...");
    final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
        destinationLauncherConfig.getJobId(),
        Math.toIntExact(destinationLauncherConfig.getAttemptId()),
        destinationLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getResourceRequirements());

    LOGGER.info("Setting up source...");
    // reset jobs use an empty source to induce resetting all data in destination.
    final AirbyteSource airbyteSource =
        sourceLauncherConfig.getDockerImage().equals(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB) ? new EmptyAirbyteSource()
            : new DefaultAirbyteSource(workerConfigs, sourceLauncher);

    LOGGER.info("Setting up replication worker...");
    final ReplicationWorker replicationWorker = new DefaultReplicationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        new DefaultAirbyteDestination(workerConfigs, destinationLauncher),
        new AirbyteMessageTracker(),
        new AirbyteMessageTracker());

    LOGGER.info("Running replication worker...");
    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    LOGGER.info("Sending output...");
    // this uses stdout directly because it shouldn't have the logging related prefix
    // the replication output is read from the container that launched the runner
    System.out.println(Jsons.serialize(replicationOutput));

    LOGGER.info("Replication runner complete!");
  }

  public static void main(final String[] args) throws Exception {
    WorkerHeartbeatServer heartbeatServer = null;

    try {
      // read files that contain all necessary configuration
      final String application = Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_APPLICATION));
      final Map<String, String> envMap =
          (Map<String, String>) Jsons.deserialize(Files.readString(Path.of(ReplicationLauncherWorker.INIT_FILE_ENV_MAP)), Map.class);

      final Configs configs = new EnvConfigs(envMap::get);

      heartbeatServer = new WorkerHeartbeatServer(WorkerApp.KUBE_HEARTBEAT_PORT);
      heartbeatServer.startBackground();

      if (application.equals(ReplicationLauncherWorker.REPLICATION)) {
        replicationRunner(configs);
      } else {
        LOGGER.error("Runner failed", new IllegalStateException("Unexpected value: " + application));
        System.exit(1);
      }
    } finally {
      if (heartbeatServer != null) {
        LOGGER.info("Shutting down heartbeat server...");
        heartbeatServer.stop();
      }
    }

    // required to kill kube client
    LOGGER.info("Runner closing...");
    System.exit(0);
  }

  /**
   * Creates a process builder factory that will be used to create connector containers/pods.
   */
  private static ProcessFactory getProcessBuilderFactory(final Configs configs, final WorkerConfigs workerConfigs) throws IOException {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + WorkerApp.KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getJobKubeNamespace());

      // this needs to have two ports for the source and two ports for the destination (all four must be
      // exposed)
      KubePortManagerSingleton.init(ReplicationLauncherWorker.PORTS);

      return new KubeProcessFactory(workerConfigs, configs.getJobKubeNamespace(), fabricClient, kubeHeartbeatUrl, false);
    } else {
      return new DockerProcessFactory(
          workerConfigs,
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork(),
          false);
    }
  }

}
