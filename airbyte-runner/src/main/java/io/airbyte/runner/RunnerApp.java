/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.runner;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.helpers.LogClientSingleton;
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
import io.airbyte.workers.temporal.sync.ReplicationActivityImpl;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.util.Config;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RunnerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(RunnerApp.class);

  private static void replicationRunner(final Configs configs) throws IOException, WorkerException {

    LOGGER.info("Starting replication runner app...");

    if (configs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
      KubePortManagerSingleton.init(configs.getTemporalWorkerPorts());
    }

    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);
    final ProcessFactory processFactory = getProcessBuilderFactory(configs, workerConfigs);

    LOGGER.info("Attempting to retrieve config files...");

    final JobRunConfig jobRunConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_JOB_RUN_CONFIG)), JobRunConfig.class);

    final IntegrationLauncherConfig sourceLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_SOURCE_LAUNCHER_CONFIG)), IntegrationLauncherConfig.class);

    final IntegrationLauncherConfig destinationLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_DESTINATION_LAUNCHER_CONFIG)), IntegrationLauncherConfig.class);

    final StandardSyncInput syncInput =
        Jsons.deserialize(Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_SYNC_INPUT)), StandardSyncInput.class);

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
    System.out.println(Jsons.serialize(replicationOutput));

    LOGGER.info("Replication runner complete!");
  }

  public static void main(String[] args) throws Exception {
    WorkerHeartbeatServer heartbeatServer = null;

    try {
      final String application = Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_APPLICATION));

      final Map<String, String> envMap =
          (Map<String, String>) Jsons.deserialize(Files.readString(Path.of(ReplicationActivityImpl.INIT_FILE_ENV_MAP)), Map.class);
      final Configs configs = new EnvConfigs(envMap::get);

      // set logging-related vars as properties so (at runtime) we can read these when processing
      // log4j2.xml
      setPropertyFromEnvVar(EnvConfigs.LOG_LEVEL);
      setPropertyFromEnvVar(EnvConfigs.S3_PATH_STYLE_ACCESS);
      System.setProperty(LogClientSingleton.S3_LOG_BUCKET, configs.getLogConfigs().getS3LogBucket());
      System.setProperty(LogClientSingleton.S3_LOG_BUCKET_REGION, configs.getLogConfigs().getS3LogBucketRegion());
      System.setProperty(LogClientSingleton.AWS_ACCESS_KEY_ID, configs.getLogConfigs().getAwsAccessKey());
      System.setProperty(LogClientSingleton.AWS_SECRET_ACCESS_KEY, configs.getLogConfigs().getAwsSecretAccessKey());
      System.setProperty(LogClientSingleton.S3_MINIO_ENDPOINT, configs.getLogConfigs().getS3MinioEndpoint());
      System.setProperty(LogClientSingleton.GCP_STORAGE_BUCKET, configs.getLogConfigs().getGcpStorageBucket());
      System.setProperty(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, configs.getLogConfigs().getGoogleApplicationCredentials());

      final var logPath = LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot());
      LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(), logPath);

      heartbeatServer = new WorkerHeartbeatServer(WorkerApp.KUBE_HEARTBEAT_PORT);
      heartbeatServer.startBackground();

      if (application.equals(ReplicationActivityImpl.REPLICATION)) {
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

    // required to kill s3 logger
    LOGGER.info("Runner closing...");
    System.exit(0);
  }

  private static void setPropertyFromEnvVar(final String envVar) {
    if (System.getenv().containsKey(envVar)) {
      System.setProperty(envVar, System.getenv(envVar));
    }
  }

  private static ProcessFactory getProcessBuilderFactory(final Configs configs, final WorkerConfigs workerConfigs) throws IOException {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final ApiClient officialClient = Config.defaultClient();
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + WorkerApp.KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getKubeNamespace());
      return new KubeProcessFactory(workerConfigs, configs.getKubeNamespace(), officialClient, fabricClient, kubeHeartbeatUrl);
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
