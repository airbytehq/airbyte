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

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.temporal.TemporalUtils.TemporalJobType;
import io.airbyte.scheduler.worker_run.WorkerRun;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import java.nio.file.Path;

public class TemporalWorkerRunFactory {

  private final TemporalClient temporalClient;
  private final Path workspaceRoot;

  public TemporalWorkerRunFactory(TemporalClient temporalClient, Path workspaceRoot) {
    this.temporalClient = temporalClient;
    this.workspaceRoot = workspaceRoot;
  }

  public WorkerRun create(Job job) {
    final int attemptId = job.getAttempts().size();
    return WorkerRun.create(workspaceRoot, job.getId(), attemptId, createSupplier(job, attemptId));
  }

  public CheckedSupplier<OutputAndStatus<JobOutput>, Exception> createSupplier(Job job, int attemptId) {
    final TemporalJobType temporalJobType = Enums.convertTo(job.getConfigType(), TemporalJobType.class);
    return switch (job.getConfigType()) {
      case GET_SPEC -> () -> {
        final ConnectorSpecification connectorSpecification = temporalClient
            .submitGetSpec(job.getId(), attemptId, job.getConfig().getGetSpec());
        final JobOutput jobOutput = new JobOutput().withGetSpec(new StandardGetSpecOutput().withSpecification(connectorSpecification));
        return new OutputAndStatus<>(JobStatus.SUCCEEDED, jobOutput);
      };
      default -> throw new IllegalArgumentException("Does not support job type: " + temporalJobType);
    };
  }

}
