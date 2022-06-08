/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import com.google.common.base.Preconditions;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.util.UUID;

public class Deployment {

  /**
   * deployment - deployment tracking info.
   */
  private final DeploymentMode deploymentMode;
  /**
   * deploymentId - Identifier for the deployment.
   *
   * This identifier tracks an install of Airbyte. Any time Airbyte is started up with new volumes or
   * persistence, it will be assigned a new deployment id. This is different from the lifecycle of the
   * rest of the data layer which may be persisted across deployments.
   */
  private final UUID deploymentId;
  /**
   * deploymentEnvironment - the environment that airbyte is running in.
   */
  private final Configs.WorkerEnvironment deploymentEnv;

  public Deployment(final DeploymentMode deploymentMode, final UUID deploymentId, final WorkerEnvironment deploymentEnv) {
    Preconditions.checkNotNull(deploymentMode);
    Preconditions.checkNotNull(deploymentId);
    Preconditions.checkNotNull(deploymentEnv);

    this.deploymentMode = deploymentMode;
    this.deploymentId = deploymentId;
    this.deploymentEnv = deploymentEnv;
  }

  public DeploymentMode getDeploymentMode() {
    return deploymentMode;
  }

  public UUID getDeploymentId() {
    return deploymentId;
  }

  public WorkerEnvironment getDeploymentEnv() {
    return deploymentEnv;
  }

}
