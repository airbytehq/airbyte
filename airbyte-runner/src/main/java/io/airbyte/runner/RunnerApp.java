/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.runner;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.*;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
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
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RunnerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(RunnerApp.class);

  private static void replicationWorker() throws IOException, WorkerException {
    // todo: is this a massive hack or the right approach?
    final Map<String, String> envMap = (Map<String, String>) Jsons.deserialize(Files.readString(Path.of("envMap.json")), Map.class);
    final Configs configs = new EnvConfigs(envMap::get);

    // won't be captured by MDC
    LOGGER.info("configs = " + configs); // todo: remove

    // set up app

    // todo: figure out where to send these logs
    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot()));

    LOGGER.info("Starting sync attempt app...");

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configs);

    final ProcessFactory processFactory = getProcessBuilderFactory(configs);

    // todo: DRY this? also present in WorkerApp
    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase).withValidation();
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configs);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, secretsHydrator, secretPersistence, ephemeralSecretPersistence);

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

  public static void main(String[] args) throws IOException {
    final String application = Files.readString(Path.of("application.txt"));

    switch (application) {
      case "replication" -> Exceptions.toRuntime(RunnerApp::replicationWorker);
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
      return new KubeProcessFactory(configs.getKubeNamespace(), officialClient, fabricClient, kubeHeartbeatUrl, configs.getTemporalWorkerPorts());
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
