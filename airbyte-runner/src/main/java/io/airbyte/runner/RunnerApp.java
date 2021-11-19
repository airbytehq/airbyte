/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.runner;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.*;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.*;
import io.airbyte.workers.process.*;
import io.airbyte.workers.protocols.airbyte.*;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.util.Config;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RunnerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(RunnerApp.class);

  private static void replicationRunner(final Configs configs) throws IOException, WorkerException {
    LOGGER.info("Starting replication runner app...");

    if (configs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
      KubePortManagerSingleton.init(configs.getTemporalWorkerPorts());
    }

    final ProcessFactory processFactory = getProcessBuilderFactory(configs);

    LOGGER.info("Attempting to retrieve files...");

    // retrieve files
    // todo: don't use magic strings
    final JobRunConfig jobRunConfig = Jsons.deserialize(Files.readString(Path.of("jobRunConfig.json")), JobRunConfig.class);

    LOGGER.info("jobRunConfig = " + jobRunConfig);

    final IntegrationLauncherConfig sourceLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of("sourceLauncherConfig.json")), IntegrationLauncherConfig.class);

    LOGGER.info("sourceLauncherConfig = " + sourceLauncherConfig);

    final IntegrationLauncherConfig destinationLauncherConfig =
        Jsons.deserialize(Files.readString(Path.of("destinationLauncherConfig.json")), IntegrationLauncherConfig.class);

    LOGGER.info("destinationLauncherConfig = " + destinationLauncherConfig);

    final StandardSyncInput syncInput = Jsons.deserialize(Files.readString(Path.of("syncInput.json")), StandardSyncInput.class);

    LOGGER.info("syncInput = " + syncInput);

    final UUID connectionId = Jsons.deserialize(Files.readString(Path.of("connectionId.json")), UUID.class); // todo: does this work?

    LOGGER.info("connectionId = " + connectionId);

    final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
        sourceLauncherConfig.getJobId(),
        Math.toIntExact(sourceLauncherConfig.getAttemptId()),
        sourceLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getResourceRequirements());
    final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
        destinationLauncherConfig.getJobId(),
        Math.toIntExact(destinationLauncherConfig.getAttemptId()),
        destinationLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getResourceRequirements());

    // reset jobs use an empty source to induce resetting all data in destination.
    final AirbyteSource airbyteSource =
        sourceLauncherConfig.getDockerImage().equals(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB) ? new EmptyAirbyteSource()
            : new DefaultAirbyteSource(sourceLauncher);

    final ReplicationWorker replicationWorker = new DefaultReplicationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        new DefaultAirbyteDestination(destinationLauncher),
        new AirbyteMessageTracker(),
        new AirbyteMessageTracker());

    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());

    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    // todo: send output on stdout for now
    System.out.println(Jsons.serialize(replicationOutput));
  }

  public static void main(String[] args) throws Exception {
    final String application = Files.readString(Path.of("application.txt"));

    final Map<String, String> envMap = (Map<String, String>) Jsons.deserialize(Files.readString(Path.of("envMap.json")), Map.class);
    final Configs configs = new EnvConfigs(envMap::get);

    if(System.getenv().containsKey("LOG_LEVEL")) {
      System.setProperty("LOG_LEVEL", System.getenv("LOG_LEVEL"));
    }

    if(System.getenv().containsKey("S3_PATH_STYLE_ACCESS")) {
      System.setProperty("S3_PATH_STYLE_ACCESS", System.getenv("S3_PATH_STYLE_ACCESS"));
    }

    System.setProperty(LogClientSingleton.S3_LOG_BUCKET, configs.getLogConfigs().getS3LogBucket());
    System.setProperty(LogClientSingleton.S3_LOG_BUCKET_REGION, configs.getLogConfigs().getS3LogBucketRegion());
    System.setProperty(LogClientSingleton.AWS_ACCESS_KEY_ID, configs.getLogConfigs().getAwsAccessKey());
    System.setProperty(LogClientSingleton.AWS_SECRET_ACCESS_KEY, configs.getLogConfigs().getAwsSecretAccessKey());
    System.setProperty(LogClientSingleton.S3_MINIO_ENDPOINT, configs.getLogConfigs().getS3MinioEndpoint());
    System.setProperty(LogClientSingleton.GCP_STORAGE_BUCKET, configs.getLogConfigs().getGcpStorageBucket());
    System.setProperty(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, configs.getLogConfigs().getGoogleApplicationCredentials());

    final var logPath = LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot());
    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(), logPath);

    switch (application) {
      case "replication" -> Exceptions.toRuntime(() -> replicationRunner(configs));
      default -> throw new IllegalStateException("Unexpected value: " + application);
    }
  }

  private static ProcessFactory getProcessBuilderFactory(final Configs configs) throws IOException {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final ApiClient officialClient = Config.defaultClient();
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + WorkerApp.KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getKubeNamespace());
      return new KubeProcessFactory(configs.getKubeNamespace(), officialClient, fabricClient, kubeHeartbeatUrl);
    } else {
      return new DockerProcessFactory(
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork(),
          false);
    }
  }

}
