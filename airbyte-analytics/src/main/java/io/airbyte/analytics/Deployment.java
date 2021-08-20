/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
