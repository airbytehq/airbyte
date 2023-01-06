/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import com.google.common.base.Splitter;
import com.google.common.base.Strings;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.TolerationPOJO;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for worker configuration-related singletons.
 */
@Factory
@Slf4j
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class WorkerConfigurationBeanFactory {

  private static final String AIRBYTE_ROLE = "AIRBYTE_ROLE";
  private static final String AIRBYTE_VERSION = "AIRBYTE_VERSION";
  private static final String DEPLOYMENT_MODE = "DEPLOYMENT_MODE";
  private static final String DOCKER = "DOCKER";
  private static final String JOB_DEFAULT_ENV_PREFIX = "JOB_DEFAULT_ENV_";
  private static final String KUBERNETES = "KUBERNETES";

  @Singleton
  @Named("checkJobKubeAnnotations")
  public Map<String, String> checkJobKubeAnnotations(@Value("${airbyte.worker.check.kube.annotations}") final String kubeAnnotations) {
    return splitKVPairsFromEnvString(kubeAnnotations);
  }

  @Singleton
  @Named("checkJobKubeNodeSelectors")
  public Map<String, String> checkJobKubeNodeSelectors(@Value("${airbyte.worker.check.kube.node-selectors}") final String kubeNodeSelectors) {
    return splitKVPairsFromEnvString(kubeNodeSelectors);
  }

  @Singleton
  @Named("discoverJobKubeAnnotations")
  public Map<String, String> discoverJobKubeAnnotations(@Value("${airbyte.worker.discover.kube.annotations}") final String kubeAnnotations) {
    return splitKVPairsFromEnvString(kubeAnnotations);
  }

  @Singleton
  @Named("discoverJobKubeNodeSelectors")
  public Map<String, String> discoverJobKubeNodeSelectors(@Value("${airbyte.worker.discover.kube.node-selectors}") final String kubeNodeSelectors) {
    return splitKVPairsFromEnvString(kubeNodeSelectors);
  }

  @Singleton
  @Named("defaultJobKubeAnnotations")
  public Map<String, String> jobKubeAnnotations(@Value("${airbyte.worker.job.kube.annotations}") final String kubeAnnotations) {
    return splitKVPairsFromEnvString(kubeAnnotations);
  }

  @Singleton
  @Named("defaultJobKubeNodeSelectors")
  public Map<String, String> jobKubeNodeSelectors(@Value("${airbyte.worker.job.kube.node-selectors}") final String kubeNodeSelectors) {
    return splitKVPairsFromEnvString(kubeNodeSelectors);
  }

  @Singleton
  @Named("specJobKubeAnnotations")
  public Map<String, String> specJobKubeAnnotations(@Value("${airbyte.worker.spec.kube.annotations}") final String kubeAnnotations) {
    return splitKVPairsFromEnvString(kubeAnnotations);
  }

  @Singleton
  @Named("isolatedNodeSelectors")
  public Map<String, String> isolatedNodeSelectors(@Value("${airbyte.worker.isolated.kube.node-selectors}") final String kubeNodeSelectors) {
    return splitKVPairsFromEnvString(kubeNodeSelectors);
  }

  @Singleton
  @Named("useCustomNodeSelector")
  public boolean useCustomNodeSelector(@Value("${airbyte.worker.isolated.kube.use-custom-node-selector}") final boolean kubeNodeSelectors) {
    return kubeNodeSelectors;
  }

  @Singleton
  @Named("specJobKubeNodeSelectors")
  public Map<String, String> specJobKubeNodeSelectors(@Value("${airbyte.worker.spec.kube.node-selectors}") final String kubeNodeSelectors) {
    return splitKVPairsFromEnvString(kubeNodeSelectors);
  }

  @Singleton
  @Named("jobDefaultEnvMap")
  public Map<String, String> jobDefaultEnvMap(
                                              @Value("${airbyte.role}") final String airbyteRole,
                                              @Value("${airbyte.version}") final String airbyteVersion,
                                              final DeploymentMode deploymentMode,
                                              final Environment environment) {
    final Map<String, String> envMap = System.getenv();
    final Map<String, String> jobPrefixedEnvMap = envMap.keySet().stream()
        .filter(key -> key.startsWith(JOB_DEFAULT_ENV_PREFIX))
        .collect(Collectors.toMap(key -> key.replace(JOB_DEFAULT_ENV_PREFIX, ""), envMap::get));
    final Map<String, String> jobSharedEnvMap = Map.of(AIRBYTE_ROLE, airbyteRole,
        AIRBYTE_VERSION, airbyteVersion,
        DEPLOYMENT_MODE, deploymentMode.name(),
        WorkerConstants.WORKER_ENVIRONMENT, environment.getActiveNames().contains(Environment.KUBERNETES) ? KUBERNETES : DOCKER);
    return MoreMaps.merge(jobPrefixedEnvMap, jobSharedEnvMap);
  }

  /**
   * Returns worker pod tolerations parsed from its own environment variable. The value of the env is
   * a string that represents one or more tolerations.
   * <ul>
   * <li>Tolerations are separated by a `;`
   * <li>Each toleration contains k=v pairs mentioning some/all of key, effect, operator and value and
   * separated by `,`
   * </ul>
   * <p>
   * For example:- The following represents two tolerations, one checking existence and another
   * matching a value
   * <p>
   * key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule
   *
   * @return list of WorkerKubeToleration parsed from env
   */
  @Singleton
  public List<TolerationPOJO> jobKubeTolerations(@Value("${airbyte.worker.job.kube.tolerations}") final String jobKubeTolerations) {
    final Stream<String> tolerations = Strings.isNullOrEmpty(jobKubeTolerations) ? Stream.of()
        : Splitter.on(";")
            .splitToStream(jobKubeTolerations)
            .filter(tolerationStr -> !Strings.isNullOrEmpty(tolerationStr));

    return tolerations
        .map(this::parseToleration)
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
  }

  @Singleton
  @Named("checkResourceRequirements")
  public ResourceRequirements checkResourceRequirements(
                                                        @Value("${airbyte.worker.check.main.container.cpu.request}") final String cpuRequest,
                                                        @Value("${airbyte.worker.check.main.container.cpu.limit}") final String cpuLimit,
                                                        @Value("${airbyte.worker.check.main.container.memory.request}") final String memoryRequest,
                                                        @Value("${airbyte.worker.check.main.container.memory.limit}") final String memoryLimit) {
    return new ResourceRequirements()
        .withCpuRequest(cpuRequest)
        .withCpuLimit(cpuLimit)
        .withMemoryRequest(memoryRequest)
        .withMemoryLimit(memoryLimit);
  }

  @Singleton
  @Named("defaultResourceRequirements")
  public ResourceRequirements defaultResourceRequirements(
                                                          @Value("${airbyte.worker.job.main.container.cpu.request}") final String cpuRequest,
                                                          @Value("${airbyte.worker.job.main.container.cpu.limit}") final String cpuLimit,
                                                          @Value("${airbyte.worker.job.main.container.memory.request}") final String memoryRequest,
                                                          @Value("${airbyte.worker.job.main.container.memory.limit}") final String memoryLimit) {
    return new ResourceRequirements()
        .withCpuRequest(cpuRequest)
        .withCpuLimit(cpuLimit)
        .withMemoryRequest(memoryRequest)
        .withMemoryLimit(memoryLimit);
  }

  @Singleton
  @Named("normalizationResourceRequirements")
  public ResourceRequirements normalizationResourceRequirements(
                                                                @Value("${airbyte.worker.normalization.main.container.cpu.request}") final String cpuRequest,
                                                                @Value("${airbyte.worker.normalization.main.container.cpu.limit}") final String cpuLimit,
                                                                @Value("${airbyte.worker.normalization.main.container.memory.request}") final String memoryRequest,
                                                                @Value("${airbyte.worker.normalization.main.container.memory.limit}") final String memoryLimit,
                                                                @Value("${airbyte.worker.job.main.container.cpu.request}") final String defaultCpuRequest,
                                                                @Value("${airbyte.worker.job.main.container.cpu.limit}") final String defaultCpuLimit,
                                                                @Value("${airbyte.worker.job.main.container.memory.request}") final String defaultMemoryRequest,
                                                                @Value("${airbyte.worker.job.main.container.memory.limit}") final String defaultMemoryLimit) {
    return new ResourceRequirements()
        .withCpuRequest(Optional.ofNullable(cpuRequest).orElse(defaultCpuRequest))
        .withCpuLimit(Optional.ofNullable(cpuLimit).orElse(defaultCpuLimit))
        .withMemoryRequest(Optional.ofNullable(memoryRequest).orElse(defaultMemoryRequest))
        .withMemoryLimit(Optional.ofNullable(memoryLimit).orElse(defaultMemoryLimit));
  }

  @Singleton
  @Named("replicationResourceRequirements")
  public ResourceRequirements replicationResourceRequirements(
                                                              @Value("${airbyte.worker.replication.orchestrator.cpu.request}") final String cpuRequest,
                                                              @Value("${airbyte.worker.replication.orchestrator.cpu.limit}") final String cpuLimit,
                                                              @Value("${airbyte.worker.replication.orchestrator.memory.request}") final String memoryRequest,
                                                              @Value("${airbyte.worker.replication.orchestrator.memory.limit}") final String memoryLimit) {
    return new ResourceRequirements()
        .withCpuRequest(cpuRequest)
        .withCpuLimit(cpuLimit)
        .withMemoryRequest(memoryRequest)
        .withMemoryLimit(memoryLimit);
  }

  void validateIsolatedPoolConfigInitialization(boolean useCustomNodeSelector, Map<String, String> isolatedNodeSelectors) {
    if (useCustomNodeSelector && isolatedNodeSelectors.isEmpty()) {
      throw new RuntimeException("Isolated Node selectors is empty while useCustomNodeSelector is set to true.");
    }
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("checkWorkerConfigs")
  public WorkerConfigs checkWorkerConfigs(
                                          final WorkerEnvironment workerEnvironment,
                                          @Named("checkResourceRequirements") final ResourceRequirements resourceRequirements,
                                          final List<TolerationPOJO> jobKubeTolerations,
                                          @Named("checkJobKubeNodeSelectors") final Map<String, String> nodeSelectors,
                                          @Named("isolatedNodeSelectors") final Map<String, String> isolatedNodeSelectors,
                                          @Named("useCustomNodeSelector") final boolean useCustomNodeSelector,
                                          @Named("checkJobKubeAnnotations") final Map<String, String> annotations,
                                          @Value("${airbyte.worker.job.kube.main.container.image-pull-secret}") final List<String> mainContainerImagePullSecret,
                                          @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String mainContainerImagePullPolicy,
                                          @Value("${airbyte.worker.job.kube.sidecar.container.image-pull-policy}") final String sidecarContainerImagePullPolicy,
                                          @Value("${airbyte.worker.job.kube.images.socat}") final String socatImage,
                                          @Value("${airbyte.worker.job.kube.images.busybox}") final String busyboxImage,
                                          @Value("${airbyte.worker.job.kube.images.curl}") final String curlImage,
                                          @Named("jobDefaultEnvMap") final Map<String, String> jobDefaultEnvMap) {
    validateIsolatedPoolConfigInitialization(useCustomNodeSelector, isolatedNodeSelectors);
    return new WorkerConfigs(
        workerEnvironment,
        resourceRequirements,
        jobKubeTolerations,
        nodeSelectors,
        useCustomNodeSelector ? Optional.of(isolatedNodeSelectors) : Optional.empty(),
        annotations,
        mainContainerImagePullSecret,
        mainContainerImagePullPolicy,
        sidecarContainerImagePullPolicy,
        socatImage,
        busyboxImage,
        curlImage,
        jobDefaultEnvMap);
  }

  @Singleton
  @Named("defaultWorkerConfigs")
  public WorkerConfigs defaultWorkerConfigs(
                                            final WorkerEnvironment workerEnvironment,
                                            @Named("defaultResourceRequirements") final ResourceRequirements resourceRequirements,
                                            final List<TolerationPOJO> jobKubeTolerations,
                                            @Named("defaultJobKubeNodeSelectors") final Map<String, String> nodeSelectors,
                                            @Named("isolatedNodeSelectors") final Map<String, String> isolatedNodeSelectors,
                                            @Named("useCustomNodeSelector") final boolean useCustomNodeSelector,
                                            @Named("defaultJobKubeAnnotations") final Map<String, String> annotations,
                                            @Value("${airbyte.worker.job.kube.main.container.image-pull-secret}") final List<String> mainContainerImagePullSecret,
                                            @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String mainContainerImagePullPolicy,
                                            @Value("${airbyte.worker.job.kube.sidecar.container.image-pull-policy}") final String sidecarContainerImagePullPolicy,
                                            @Value("${airbyte.worker.job.kube.images.socat}") final String socatImage,
                                            @Value("${airbyte.worker.job.kube.images.busybox}") final String busyboxImage,
                                            @Value("${airbyte.worker.job.kube.images.curl}") final String curlImage,
                                            @Named("jobDefaultEnvMap") final Map<String, String> jobDefaultEnvMap) {
    validateIsolatedPoolConfigInitialization(useCustomNodeSelector, isolatedNodeSelectors);
    return new WorkerConfigs(
        workerEnvironment,
        resourceRequirements,
        jobKubeTolerations,
        nodeSelectors,
        useCustomNodeSelector ? Optional.of(isolatedNodeSelectors) : Optional.empty(),
        annotations,
        mainContainerImagePullSecret,
        mainContainerImagePullPolicy,
        sidecarContainerImagePullPolicy,
        socatImage,
        busyboxImage,
        curlImage,
        jobDefaultEnvMap);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("discoverWorkerConfigs")
  public WorkerConfigs discoverWorkerConfigs(
                                             final WorkerEnvironment workerEnvironment,
                                             @Named("defaultResourceRequirements") final ResourceRequirements resourceRequirements,
                                             final List<TolerationPOJO> jobKubeTolerations,
                                             @Named("discoverJobKubeNodeSelectors") final Map<String, String> nodeSelectors,
                                             @Named("isolatedNodeSelectors") final Map<String, String> isolatedNodeSelectors,
                                             @Named("useCustomNodeSelector") final boolean useCustomNodeSelector,
                                             @Named("discoverJobKubeAnnotations") final Map<String, String> annotations,
                                             @Value("${airbyte.worker.job.kube.main.container.image-pull-secret}") final List<String> mainContainerImagePullSecret,
                                             @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String mainContainerImagePullPolicy,
                                             @Value("${airbyte.worker.job.kube.sidecar.container.image-pull-policy}") final String sidecarContainerImagePullPolicy,
                                             @Value("${airbyte.worker.job.kube.images.socat}") final String socatImage,
                                             @Value("${airbyte.worker.job.kube.images.busybox}") final String busyboxImage,
                                             @Value("${airbyte.worker.job.kube.images.curl}") final String curlImage,
                                             @Named("jobDefaultEnvMap") final Map<String, String> jobDefaultEnvMap) {
    validateIsolatedPoolConfigInitialization(useCustomNodeSelector, isolatedNodeSelectors);
    return new WorkerConfigs(
        workerEnvironment,
        resourceRequirements,
        jobKubeTolerations,
        nodeSelectors,
        useCustomNodeSelector ? Optional.of(isolatedNodeSelectors) : Optional.empty(),
        annotations,
        mainContainerImagePullSecret,
        mainContainerImagePullPolicy,
        sidecarContainerImagePullPolicy,
        socatImage,
        busyboxImage,
        curlImage,
        jobDefaultEnvMap);
  }

  @Singleton
  @Named("replicationWorkerConfigs")
  public WorkerConfigs replicationWorkerConfigs(
                                                final WorkerEnvironment workerEnvironment,
                                                @Named("replicationResourceRequirements") final ResourceRequirements resourceRequirements,
                                                final List<TolerationPOJO> jobKubeTolerations,
                                                @Named("defaultJobKubeNodeSelectors") final Map<String, String> nodeSelectors,
                                                @Named("isolatedNodeSelectors") final Map<String, String> isolatedNodeSelectors,
                                                @Named("useCustomNodeSelector") final boolean useCustomNodeSelector,
                                                @Named("defaultJobKubeAnnotations") final Map<String, String> annotations,
                                                @Value("${airbyte.worker.job.kube.main.container.image-pull-secret}") final List<String> mainContainerImagePullSecret,
                                                @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String mainContainerImagePullPolicy,
                                                @Value("${airbyte.worker.job.kube.sidecar.container.image-pull-policy}") final String sidecarContainerImagePullPolicy,
                                                @Value("${airbyte.worker.job.kube.images.socat}") final String socatImage,
                                                @Value("${airbyte.worker.job.kube.images.busybox}") final String busyboxImage,
                                                @Value("${airbyte.worker.job.kube.images.curl}") final String curlImage,
                                                @Named("jobDefaultEnvMap") final Map<String, String> jobDefaultEnvMap) {
    validateIsolatedPoolConfigInitialization(useCustomNodeSelector, isolatedNodeSelectors);
    return new WorkerConfigs(
        workerEnvironment,
        resourceRequirements,
        jobKubeTolerations,
        nodeSelectors,
        useCustomNodeSelector ? Optional.of(isolatedNodeSelectors) : Optional.empty(),
        annotations,
        mainContainerImagePullSecret,
        mainContainerImagePullPolicy,
        sidecarContainerImagePullPolicy,
        socatImage,
        busyboxImage,
        curlImage,
        jobDefaultEnvMap);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("specWorkerConfigs")
  public WorkerConfigs specWorkerConfigs(
                                         final WorkerEnvironment workerEnvironment,
                                         @Named("defaultResourceRequirements") final ResourceRequirements resourceRequirements,
                                         final List<TolerationPOJO> jobKubeTolerations,
                                         @Named("specJobKubeNodeSelectors") final Map<String, String> nodeSelectors,
                                         @Named("isolatedNodeSelectors") final Map<String, String> isolatedNodeSelectors,
                                         @Named("useCustomNodeSelector") final boolean useCustomNodeSelector,
                                         @Named("specJobKubeAnnotations") final Map<String, String> annotations,
                                         @Value("${airbyte.worker.job.kube.main.container.image-pull-secret}") final List<String> mainContainerImagePullSecret,
                                         @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String mainContainerImagePullPolicy,
                                         @Value("${airbyte.worker.job.kube.sidecar.container.image-pull-policy}") final String sidecarContainerImagePullPolicy,
                                         @Value("${airbyte.worker.job.kube.images.socat}") final String socatImage,
                                         @Value("${airbyte.worker.job.kube.images.busybox}") final String busyboxImage,
                                         @Value("${airbyte.worker.job.kube.images.curl}") final String curlImage,
                                         @Named("jobDefaultEnvMap") final Map<String, String> jobDefaultEnvMap) {
    validateIsolatedPoolConfigInitialization(useCustomNodeSelector, isolatedNodeSelectors);
    return new WorkerConfigs(
        workerEnvironment,
        resourceRequirements,
        jobKubeTolerations,
        nodeSelectors,
        useCustomNodeSelector ? Optional.of(isolatedNodeSelectors) : Optional.empty(),
        annotations,
        mainContainerImagePullSecret,
        mainContainerImagePullPolicy,
        sidecarContainerImagePullPolicy,
        socatImage,
        busyboxImage,
        curlImage,
        jobDefaultEnvMap);
  }

  /**
   * Splits key value pairs from the input string into a map. Each kv-pair is separated by a ','. The
   * key and the value are separated by '='.
   * <p>
   * For example:- The following represents two map entries
   * </p>
   * key1=value1,key2=value2
   *
   * @param input string
   * @return map containing kv pairs
   */
  private Map<String, String> splitKVPairsFromEnvString(final String input) {
    return Splitter.on(",")
        .splitToStream(input)
        .filter(s -> !Strings.isNullOrEmpty(s) && s.contains("="))
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0].trim(), s -> s[1].trim()));
  }

  private TolerationPOJO parseToleration(final String tolerationStr) {
    final Map<String, String> tolerationMap = Splitter.on(",")
        .splitToStream(tolerationStr)
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0], s -> s[1]));

    if (tolerationMap.containsKey("key") && tolerationMap.containsKey("effect") && tolerationMap.containsKey("operator")) {
      return new TolerationPOJO(
          tolerationMap.get("key"),
          tolerationMap.get("effect"),
          tolerationMap.get("value"),
          tolerationMap.get("operator"));
    } else {
      log.warn(
          "Ignoring toleration {}, missing one of key,effect or operator",
          tolerationStr);
      return null;
    }
  }

}
