/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.file.Path;

/**
 * Micronaut bean factory for process factory-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class ProcessFactoryBeanFactory {

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(notEnv = Environment.KUBERNETES)
  @Named("checkProcessFactory")
  public ProcessFactory checkDockerProcessFactory(
                                                  @Named("checkWorkerConfigs") final WorkerConfigs workerConfigs,
                                                  @Value("${docker.network}") final String dockerNetwork,
                                                  @Value("${airbyte.local.docker-mount}") final String localDockerMount,
                                                  @Value("${airbyte.local.root}") final String localRoot,
                                                  @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
                                                  @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return createDockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        localRoot,
        dockerNetwork);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(env = Environment.KUBERNETES)
  @Named("checkProcessFactory")
  public ProcessFactory checkKubernetesProcessFactory(
                                                      @Named("checkWorkerConfigs") final WorkerConfigs workerConfigs,
                                                      @Value("${airbyte.worker.job.kube.namespace}") final String kubernetesNamespace,
                                                      @Value("${micronaut.server.port}") final Integer serverPort)
      throws UnknownHostException {
    return createKubernetesProcessFactory(workerConfigs,
        kubernetesNamespace,
        serverPort);
  }

  @Singleton
  @Requires(notEnv = Environment.KUBERNETES)
  @Named("defaultProcessFactory")
  public ProcessFactory defaultDockerProcessFactory(
                                                    @Named("defaultWorkerConfigs") final WorkerConfigs workerConfigs,
                                                    @Value("${docker.network}") final String dockerNetwork,
                                                    @Value("${airbyte.local.docker-mount}") final String localDockerMount,
                                                    @Value("${airbyte.local.root}") final String localRoot,
                                                    @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
                                                    @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return createDockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        localRoot,
        dockerNetwork);
  }

  @Singleton
  @Requires(env = Environment.KUBERNETES)
  @Named("defaultProcessFactory")
  public ProcessFactory defaultKubernetesProcessFactory(
                                                        @Named("defaultWorkerConfigs") final WorkerConfigs workerConfigs,
                                                        @Value("${airbyte.worker.job.kube.namespace}") final String kubernetesNamespace,
                                                        @Value("${micronaut.server.port}") final Integer serverPort)
      throws UnknownHostException {
    return createKubernetesProcessFactory(workerConfigs,
        kubernetesNamespace,
        serverPort);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(notEnv = Environment.KUBERNETES)
  @Named("discoverProcessFactory")
  public ProcessFactory discoverDockerProcessFactory(
                                                     @Named("discoverWorkerConfigs") final WorkerConfigs workerConfigs,
                                                     @Value("${docker.network}") final String dockerNetwork,
                                                     @Value("${airbyte.local.docker-mount}") final String localDockerMount,
                                                     @Value("${airbyte.local.root}") final String localRoot,
                                                     @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
                                                     @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return createDockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        localRoot,
        dockerNetwork);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(env = Environment.KUBERNETES)
  @Named("discoverProcessFactory")
  public ProcessFactory discoverKubernetesProcessFactory(
                                                         @Named("discoverWorkerConfigs") final WorkerConfigs workerConfigs,
                                                         @Value("${airbyte.worker.job.kube.namespace}") final String kubernetesNamespace,
                                                         @Value("${micronaut.server.port}") final Integer serverPort)
      throws UnknownHostException {
    return createKubernetesProcessFactory(workerConfigs,
        kubernetesNamespace,
        serverPort);
  }

  @Singleton
  @Requires(notEnv = Environment.KUBERNETES)
  @Named("replicationProcessFactory")
  public ProcessFactory replicationDockerProcessFactory(
                                                        @Named("replicationWorkerConfigs") final WorkerConfigs workerConfigs,
                                                        @Value("${docker.network}") final String dockerNetwork,
                                                        @Value("${airbyte.local.docker-mount}") final String localDockerMount,
                                                        @Value("${airbyte.local.root}") final String localRoot,
                                                        @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
                                                        @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return createDockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        localRoot,
        dockerNetwork);
  }

  @Singleton
  @Requires(env = Environment.KUBERNETES)
  @Named("replicationProcessFactory")
  public ProcessFactory replicationKubernetesProcessFactory(
                                                            @Named("replicationWorkerConfigs") final WorkerConfigs workerConfigs,
                                                            @Value("${airbyte.worker.job.kube.namespace}") final String kubernetesNamespace,
                                                            @Value("${micronaut.server.port}") final Integer serverPort)
      throws UnknownHostException {
    return createKubernetesProcessFactory(workerConfigs,
        kubernetesNamespace,
        serverPort);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(notEnv = Environment.KUBERNETES)
  @Named("specProcessFactory")
  public ProcessFactory specDockerProcessFactory(
                                                 @Named("specWorkerConfigs") final WorkerConfigs workerConfigs,
                                                 @Value("${docker.network}") final String dockerNetwork,
                                                 @Value("${airbyte.local.docker-mount}") final String localDockerMount,
                                                 @Value("${airbyte.local.root}") final String localRoot,
                                                 @Value("${airbyte.workspace.docker-mount}") final String workspaceDockerMount,
                                                 @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return createDockerProcessFactory(
        workerConfigs,
        Path.of(workspaceRoot),
        workspaceDockerMount,
        localDockerMount,
        localRoot,
        dockerNetwork);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Requires(env = Environment.KUBERNETES)
  @Named("specProcessFactory")
  public ProcessFactory specKubernetesProcessFactory(
                                                     @Named("specWorkerConfigs") final WorkerConfigs workerConfigs,
                                                     @Value("${airbyte.worker.job.kube.namespace}") final String kubernetesNamespace,
                                                     @Value("${micronaut.server.port}") final Integer serverPort)
      throws UnknownHostException {
    return createKubernetesProcessFactory(workerConfigs,
        kubernetesNamespace,
        serverPort);
  }

  private ProcessFactory createDockerProcessFactory(final WorkerConfigs workerConfigs,
                                                    final Path workspaceRoot,
                                                    final String workspaceDockerMount,
                                                    final String localDockerMount,
                                                    final String localRoot,
                                                    final String dockerNetwork) {
    return new DockerProcessFactory(
        workerConfigs,
        workspaceRoot,
        StringUtils.isNotEmpty(workspaceDockerMount) ? workspaceDockerMount : workspaceRoot.toString(),
        StringUtils.isNotEmpty(localDockerMount) ? localDockerMount : localRoot,
        dockerNetwork);
  }

  private ProcessFactory createKubernetesProcessFactory(final WorkerConfigs workerConfigs,
                                                        final String kubernetesNamespace,
                                                        final Integer serverPort)
      throws UnknownHostException {
    final KubernetesClient fabricClient = new DefaultKubernetesClient();
    final String localIp = InetAddress.getLocalHost().getHostAddress();
    final String kubeHeartbeatUrl = localIp + ":" + serverPort;
    return new KubeProcessFactory(workerConfigs,
        kubernetesNamespace,
        fabricClient,
        kubeHeartbeatUrl,
        false);
  }

}
