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

package io.airbyte.scheduler.temporal;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.IntegrationLauncherConfig;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.temporal.TemporalUtils.TemporalJobType;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.client.WorkflowClient;

public class TemporalClient {

  private final WorkflowClient client;

  public TemporalClient(WorkflowClient client) {
    this.client = client;
  }

  public OutputAndStatus<JobOutput> submitGetSpec(long jobId, int attempt, JobGetSpecConfig config) {
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId)
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    return toOutputAndStatus(() -> getWorkflowStub(SpecWorkflow.class, TemporalJobType.GET_SPEC).run(launcherConfig));

  }

  public OutputAndStatus<JobOutput> submitCheckConnection(long jobId, int attempt, JobCheckConnectionConfig config) {
    final StandardCheckConnectionInput input = new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId)
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());

    return toOutputAndStatus(() -> getWorkflowStub(CheckConnectionWorkflow.class, TemporalJobType.CHECK_CONNECTION).run(launcherConfig, input));
  }

  public OutputAndStatus<JobOutput> submitDiscoverSchema(long jobId, int attempt, JobDiscoverCatalogConfig config) {
    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration());
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId)
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());

    return toOutputAndStatus(() -> getWorkflowStub(DiscoverCatalogWorkflow.class, TemporalJobType.DISCOVER_SCHEMA).run(launcherConfig, input));
  }

  public OutputAndStatus<JobOutput> submitSync(long jobId, int attempt, JobSyncConfig config) {
    final StandardSyncInput input = new StandardSyncInput()
        .withDefaultNamespace(config.getDefaultNamespace())
        .withSourceConfiguration(config.getSourceConfiguration())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog())
        .withState(config.getState());
    return toOutputAndStatus(() -> getWorkflowStub(SyncWorkflow.class, TemporalJobType.SYNC).run(
        jobId,
        attempt,
        config.getSourceDockerImage(),
        config.getDestinationDockerImage(),
        input));
  }

  private OutputAndStatus<JobOutput> toOutputAndStatus(CheckedSupplier<JobOutput, TemporalJobException> supplier) {
    try {
      return new OutputAndStatus<>(JobStatus.SUCCEEDED, supplier.get());
    } catch (TemporalJobException e) {
      return new OutputAndStatus<>(JobStatus.FAILED);
    }
  }

  private <T> T getWorkflowStub(Class<T> workflowClass, TemporalJobType jobType) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptions(jobType));
  }

}
