/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.fabric8.kubernetes.client.KubernetesClient;

public record ContainerOrchestratorConfig(
                                          String namespace,
                                          DocumentStoreClient documentStoreClient,
                                          KubernetesClient kubernetesClient,
                                          String secretName,
                                          String secretMountPath,
                                          String containerOrchestratorImage,
                                          String containerOrchestratorImagePullPolicy,
                                          String googleApplicationCredentials,
                                          WorkerEnvironment workerEnvironment) {}
