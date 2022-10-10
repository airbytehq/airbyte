/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.worker;

import io.airbyte.commons.worker.storage.DocumentStoreClient;
import io.airbyte.config.Configs.WorkerEnvironment;
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
