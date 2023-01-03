/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

public record KubePodInfo(String namespace, String name, KubeContainerInfo mainContainerInfo) {}
