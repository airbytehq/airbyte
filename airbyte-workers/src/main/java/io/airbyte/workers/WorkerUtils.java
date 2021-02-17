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

package io.airbyte.workers;

import static io.airbyte.workflows.AirbyteWorkflowImpl.AIRBYTE_WORKFLOW_QUEUE;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.workflows.DiscoverCatalogWorkflow;
import io.airbyte.workflows.GetSpecWorkflow;
import io.temporal.api.enums.v1.WorkflowIdReusePolicy;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkerUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerUtils.class);

  private static final WorkflowServiceStubsOptions TEMPORAL_OPTIONS = WorkflowServiceStubsOptions.newBuilder()
      .setTarget("temporal:7233")
      .build();

  public static final WorkflowServiceStubs TEMPORAL_SERVICE = WorkflowServiceStubs.newInstance(TEMPORAL_OPTIONS);

  public static final WorkflowClient TEMPORAL_CLIENT = WorkflowClient.newInstance(TEMPORAL_SERVICE);

  public static void gentleClose(final Process process, final long timeout, final TimeUnit timeUnit) {
    if (process == null) {
      return;
    }

    try {
      process.waitFor(timeout, timeUnit);
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }
    if (process.isAlive()) {
      LOGGER.warn("Process is taking too long to finish. Killing it");
      process.destroy();
      try {
        process.waitFor(1, TimeUnit.MINUTES);
      } catch (InterruptedException e) {
        LOGGER.error("Exception while while killing the process", e);
      }
      if (process.isAlive()) {
        LOGGER.warn("Couldn't kill the process. You might have a zombie ({})", process.info().commandLine());
      }
    }
  }

  public static void closeProcess(Process process) {
    closeProcess(process, 1, TimeUnit.MINUTES);
  }

  public static void closeProcess(Process process, int duration, TimeUnit timeUnit) {
    if (process == null) {
      return;
    }
    try {
      process.destroy();
      process.waitFor(duration, timeUnit);
      if (process.isAlive()) {
        process.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when closing process.", e);
    }
  }

  public static void wait(Process process) {
    try {
      process.waitFor();
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }
  }

  public static void cancelProcess(Process process) {
    closeProcess(process, 10, TimeUnit.SECONDS);
  }

  /**
   * Translates a StandardSyncInput into a StandardTapConfig. StandardTapConfig is a subset of
   * StandardSyncInput.
   */
  public static StandardTapConfig syncToTapConfig(StandardSyncInput sync) {
    return new StandardTapConfig()
        .withSourceConnectionConfiguration(sync.getSourceConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  /**
   * Translates a StandardSyncInput into a StandardTargetConfig. StandardTargetConfig is a subset of
   * StandardSyncInput.
   */
  public static StandardTargetConfig syncToTargetConfig(StandardSyncInput sync) {
    return new StandardTargetConfig()
        .withDestinationConnectionConfiguration(sync.getDestinationConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  public static GetSpecWorkflow getSpecWorkflow(WorkflowClient workflowClient, String workflowId) {
    final WorkflowOptions options = WorkflowOptions.newBuilder()
            .setTaskQueue(AIRBYTE_WORKFLOW_QUEUE)
            .setWorkflowId(workflowId)
//        .setWorkflowIdReusePolicy(WorkflowIdReusePolicy.WORKFLOW_ID_REUSE_POLICY_UNSPECIFIED)
            .build();

    return workflowClient.newWorkflowStub(GetSpecWorkflow.class, options);
  }

  public static DiscoverCatalogWorkflow discoverCatalogWorkflow(WorkflowClient workflowClient, String workflowId) {
    final WorkflowOptions options = WorkflowOptions.newBuilder()
            .setTaskQueue(AIRBYTE_WORKFLOW_QUEUE)
            .setWorkflowId(workflowId)
//        .setWorkflowIdReusePolicy(WorkflowIdReusePolicy.WORKFLOW_ID_REUSE_POLICY_UNSPECIFIED)
            .build();

    return workflowClient.newWorkflowStub(DiscoverCatalogWorkflow.class, options);
  }

}
