/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.util.Map;

public record ContainerOrchestratorConfig(
                                          String namespace,
                                          DocumentStoreClient documentStoreClient,
                                          Map<String, String> environmentVariables,
                                          KubernetesClient kubernetesClient,
                                          String secretName,
                                          String secretMountPath,
                                          String dataPlaneCredsSecretName,
                                          String dataPlaneCredsSecretMountPath,
                                          String containerOrchestratorImage,
                                          String containerOrchestratorImagePullPolicy,
                                          String googleApplicationCredentials,
                                          WorkerEnvironment workerEnvironment) {}
