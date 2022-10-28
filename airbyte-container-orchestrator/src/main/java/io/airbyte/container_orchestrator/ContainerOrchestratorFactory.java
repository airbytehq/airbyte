/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.temporal.sync.OrchestratorConstants;
import io.airbyte.config.EnvConfigs;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.sync.DbtLauncherWorker;
import io.airbyte.workers.sync.NormalizationLauncherWorker;
import io.airbyte.workers.sync.ReplicationLauncherWorker;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.file.Path;
import java.util.Map;

@Factory
class ContainerOrchestratorFactory {

  @Singleton
  String application() throws IOException {
    return "NO_OP";
//    return Files.readString(
//        Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_APPLICATION));
  }

  @Singleton
  Map<String, String> env() {
    return Map.of();
//    return Jsons.deserialize(
//        Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_ENV_MAP).toFile(),
//        new TypeReference<>() {
//        });
  }

  @Singleton
  JobRunConfig jobRunConfig() {
    return new JobRunConfig().withJobId("1").withAttemptId(2L);
//    return Jsons.deserialize(
//        Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG)
//            .toFile(),
//        JobRunConfig.class);
  }

  @Singleton
  KubePodInfo kubePodInfo() {
    return new KubePodInfo("namespace", "name", null);
//    return Jsons.deserialize(
//        Path.of(KubePodProcess.CONFIG_DIR, AsyncOrchestratorPodProcess.KUBE_POD_INFO).toFile(),
//        KubePodInfo.class);
  }

  @Singleton
  FeatureFlags featureFlags() {
    return new EnvVariableFeatureFlags();
  }

  @Singleton
  EnvConfigs envConfigs(final Map<String, String> env) {
    return new EnvConfigs(env);
  }

  @Singleton
  WorkerConfigs workerConfigs(final EnvConfigs envConfigs) {
    return new WorkerConfigs(envConfigs);
  }

  @Singleton
  @Requires(notEnv = Environment.KUBERNETES)
  ProcessFactory dockerProcessFactory(
      final WorkerConfigs workerConfigs,
      @Value("${airbyte.workspace.root}") final String workspaceRoot,
      @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
      @Value("${airbyte.local.docker-mount}") final String localDockerMount,
      @Value("${airbyte.local.root}") final String localRoot,
      @Value("${docker.network}") final String dockerNetwork
  ) {
    return new DockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        dockerNetwork
    );
  }

  @Singleton
  @Requires(env = Environment.KUBERNETES)
  ProcessFactory kubeProcessFactory(
      final WorkerConfigs workerConfigs,
      @Value("${airbyte.worker.job.kube.namespace}") final String k8sNamespace,
      @Value("${micronaut.server.port}") final int serverPort
  ) throws UnknownHostException {
    final var localIp = InetAddress.getLocalHost().getHostAddress();
    final var kubeHeartbeatUrl = localIp + ":" + serverPort;

    // this needs to have two ports for the source and two ports for the destination (all four must be
    // exposed)
    KubePortManagerSingleton.init(OrchestratorConstants.PORTS);

    return new KubeProcessFactory(workerConfigs,
        k8sNamespace,
        new DefaultKubernetesClient(),
        kubeHeartbeatUrl,
        false);
  }

  @Singleton
  JobOrchestrator<?> jobOrchestrator(
      final String application,
      final EnvConfigs envConfigs,
      final ProcessFactory processFactory,
      final FeatureFlags featureFlags,
      final WorkerConfigs workerConfigs
  ) {
    return switch (application) {
      case ReplicationLauncherWorker.REPLICATION ->
          new ReplicationJobOrchestrator(envConfigs, processFactory, featureFlags);
      case NormalizationLauncherWorker.NORMALIZATION ->
          new NormalizationJobOrchestrator(envConfigs, processFactory);
      case DbtLauncherWorker.DBT ->
          new DbtJobOrchestrator(envConfigs, workerConfigs, processFactory);
      case AsyncOrchestratorPodProcess.NO_OP -> new NoOpOrchestrator();
      default -> throw new IllegalStateException(
          "Could not find job orchestrator for application: " + application);
    };
  }

}
