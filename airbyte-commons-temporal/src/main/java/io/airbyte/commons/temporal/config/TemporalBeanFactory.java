/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.config;

import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.nio.file.Path;

/**
 * Micronaut bean factory for Temporal-related singletons.
 */
@Factory
public class TemporalBeanFactory {

  @Singleton
  public WorkflowServiceStubs temporalService(final TemporalUtils temporalUtils) {
    return temporalUtils.createTemporalService();
  }

  @Singleton
  public WorkflowClient workflowClient(
                                       final TemporalUtils temporalUtils,
                                       final WorkflowServiceStubs temporalService) {
    return TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace());
  }

  @Singleton
  @Named("workspaceRootTemporal")
  public Path workspaceRoot(@Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return Path.of(workspaceRoot);
  }

}
