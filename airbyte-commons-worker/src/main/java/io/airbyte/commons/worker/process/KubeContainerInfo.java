/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.worker.process;

public record KubeContainerInfo(String image, String pullPolicy) {}
