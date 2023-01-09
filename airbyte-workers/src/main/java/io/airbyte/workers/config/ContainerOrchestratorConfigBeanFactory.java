/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.airbyte.workers.storage.StateClients;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Micronaut bean factory for container orchestrator configuration-related singletons.
 */
@Factory
public class ContainerOrchestratorConfigBeanFactory {

  private static final String METRIC_CLIENT_ENV_VAR = "METRIC_CLIENT";
  private static final String DD_AGENT_HOST_ENV_VAR = "DD_AGENT_HOST";
  private static final String DD_DOGSTATSD_PORT_ENV_VAR = "DD_DOGSTATSD_PORT";
  private static final String DD_ENV_ENV_VAR = "DD_ENV";
  private static final String DD_SERVICE_ENV_VAR = "DD_SERVICE";
  private static final String DD_VERSION_ENV_VAR = "DD_VERSION";
  private static final String JAVA_OPTS_ENV_VAR = "JAVA_OPTS";
  private static final String PUBLISH_METRICS_ENV_VAR = "PUBLISH_METRICS";
  private static final String CONTROL_PLANE_AUTH_ENDPOINT_ENV_VAR = "CONTROL_PLANE_AUTH_ENDPOINT";
  private static final String DATA_PLANE_SERVICE_ACCOUNT_CREDENTIALS_PATH_ENV_VAR = "DATA_PLANE_SERVICE_ACCOUNT_CREDENTIALS_PATH";
  private static final String DATA_PLANE_SERVICE_ACCOUNT_EMAIL_ENV_VAR = "DATA_PLANE_SERVICE_ACCOUNT_EMAIL";
  private static final String AIRBYTE_API_AUTH_HEADER_NAME_ENV_VAR = "AIRBYTE_API_AUTH_HEADER_NAME";
  private static final String AIRBYTE_API_AUTH_HEADER_VALUE_ENV_VAR = "AIRBYTE_API_AUTH_HEADER_VALUE";
  private static final String INTERNAL_API_HOST_ENV_VAR = "INTERNAL_API_HOST";

  // IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
  // version is deployed!
  private static final Path STATE_STORAGE_PREFIX = Path.of("/state");

  @Singleton
  @Requires(property = "airbyte.container.orchestrator.enabled",
            value = "true")
  @Named("containerOrchestratorConfig")
  public ContainerOrchestratorConfig kubernetesContainerOrchestratorConfig(
                                                                           @Named("stateStorageConfigs") final Optional<CloudStorageConfigs> cloudStateStorageConfiguration,
                                                                           @Value("${airbyte.version}") final String airbyteVersion,
                                                                           @Value("${airbyte.container.orchestrator.image}") final String containerOrchestratorImage,
                                                                           @Value("${airbyte.worker.job.kube.main.container.image-pull-policy}") final String containerOrchestratorImagePullPolicy,
                                                                           @Value("${airbyte.container.orchestrator.secret-mount-path}") final String containerOrchestratorSecretMountPath,
                                                                           @Value("${airbyte.container.orchestrator.secret-name}") final String containerOrchestratorSecretName,
                                                                           @Value("${google.application.credentials}") final String googleApplicationCredentials,
                                                                           @Value("${airbyte.worker.job.kube.namespace}") final String namespace,
                                                                           @Value("${airbyte.metric.client}") final String metricClient,
                                                                           @Value("${datadog.agent.host}") final String dataDogAgentHost,
                                                                           @Value("${datadog.agent.port}") final String dataDogStatsdPort,
                                                                           @Value("${airbyte.metric.should-publish}") final String shouldPublishMetrics,
                                                                           final FeatureFlags featureFlags,
                                                                           @Value("${airbyte.container.orchestrator.java-opts}") final String containerOrchestratorJavaOpts,
                                                                           final WorkerEnvironment workerEnvironment,
                                                                           @Value("${airbyte.internal.api.host}") final String containerOrchestratorApiHost,
                                                                           @Value("${airbyte.internal.api.auth-header.name}") final String containerOrchestratorApiAuthHeaderName,
                                                                           @Value("${airbyte.internal.api.auth-header.value}") final String containerOrchestratorApiAuthHeaderValue,
                                                                           @Value("${airbyte.control.plane.auth-endpoint}") final String controlPlaneAuthEndpoint,
                                                                           @Value("${airbyte.data.plane.service-account.email}") final String dataPlaneServiceAccountEmail,
                                                                           @Value("${airbyte.data.plane.service-account.credentials-path}") final String dataPlaneServiceAccountCredentialsPath,
                                                                           @Value("${airbyte.container.orchestrator.data-plane-creds.secret-mount-path}") final String containerOrchestratorDataPlaneCredsSecretMountPath,
                                                                           @Value("${airbyte.container.orchestrator.data-plane-creds.secret-name}") final String containerOrchestratorDataPlaneCredsSecretName) {
    final var kubernetesClient = new DefaultKubernetesClient();

    final DocumentStoreClient documentStoreClient = StateClients.create(
        cloudStateStorageConfiguration.orElse(null),
        STATE_STORAGE_PREFIX);

    // Build the map of additional environment variables to be passed to the container orchestrator
    final Map<String, String> environmentVariables = new HashMap<>();
    environmentVariables.put(METRIC_CLIENT_ENV_VAR, metricClient);
    environmentVariables.put(DD_AGENT_HOST_ENV_VAR, dataDogAgentHost);
    environmentVariables.put(DD_SERVICE_ENV_VAR, "airbyte-container-orchestrator");
    environmentVariables.put(DD_DOGSTATSD_PORT_ENV_VAR, dataDogStatsdPort);
    environmentVariables.put(PUBLISH_METRICS_ENV_VAR, shouldPublishMetrics);
    environmentVariables.put(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, Boolean.toString(featureFlags.useStreamCapableState()));
    environmentVariables.put(EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA, Boolean.toString(featureFlags.autoDetectSchema()));
    environmentVariables.put(EnvVariableFeatureFlags.APPLY_FIELD_SELECTION, Boolean.toString(featureFlags.applyFieldSelection()));
    environmentVariables.put(EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES, featureFlags.fieldSelectionWorkspaces());
    environmentVariables.put(JAVA_OPTS_ENV_VAR, containerOrchestratorJavaOpts);
    environmentVariables.put(CONTROL_PLANE_AUTH_ENDPOINT_ENV_VAR, controlPlaneAuthEndpoint);
    environmentVariables.put(DATA_PLANE_SERVICE_ACCOUNT_CREDENTIALS_PATH_ENV_VAR, dataPlaneServiceAccountCredentialsPath);
    environmentVariables.put(DATA_PLANE_SERVICE_ACCOUNT_EMAIL_ENV_VAR, dataPlaneServiceAccountEmail);

    if (System.getenv(DD_ENV_ENV_VAR) != null) {
      environmentVariables.put(DD_ENV_ENV_VAR, System.getenv(DD_ENV_ENV_VAR));
    }

    if (System.getenv(DD_VERSION_ENV_VAR) != null) {
      environmentVariables.put(DD_VERSION_ENV_VAR, System.getenv(DD_VERSION_ENV_VAR));
    }

    // Environment variables for ApiClientBeanFactory
    environmentVariables.put(CONTROL_PLANE_AUTH_ENDPOINT_ENV_VAR, controlPlaneAuthEndpoint);
    environmentVariables.put(DATA_PLANE_SERVICE_ACCOUNT_CREDENTIALS_PATH_ENV_VAR, dataPlaneServiceAccountCredentialsPath);
    environmentVariables.put(DATA_PLANE_SERVICE_ACCOUNT_EMAIL_ENV_VAR, dataPlaneServiceAccountEmail);
    environmentVariables.put(AIRBYTE_API_AUTH_HEADER_NAME_ENV_VAR, containerOrchestratorApiAuthHeaderName);
    environmentVariables.put(AIRBYTE_API_AUTH_HEADER_VALUE_ENV_VAR, containerOrchestratorApiAuthHeaderValue);
    environmentVariables.put(INTERNAL_API_HOST_ENV_VAR, containerOrchestratorApiHost);

    if (System.getenv(Environment.ENVIRONMENTS_ENV) != null) {
      environmentVariables.put(Environment.ENVIRONMENTS_ENV, System.getenv(Environment.ENVIRONMENTS_ENV));
    }

    return new ContainerOrchestratorConfig(
        namespace,
        documentStoreClient,
        environmentVariables,
        kubernetesClient,
        containerOrchestratorSecretName,
        containerOrchestratorSecretMountPath,
        containerOrchestratorDataPlaneCredsSecretName,
        containerOrchestratorDataPlaneCredsSecretMountPath,
        StringUtils.isNotEmpty(containerOrchestratorImage) ? containerOrchestratorImage : "airbyte/container-orchestrator:" + airbyteVersion,
        containerOrchestratorImagePullPolicy,
        googleApplicationCredentials,
        workerEnvironment);
  }

}
