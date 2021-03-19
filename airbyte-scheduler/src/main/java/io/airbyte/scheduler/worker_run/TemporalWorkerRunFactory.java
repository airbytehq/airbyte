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

package io.airbyte.scheduler.worker_run;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.Job;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobException;
import io.airbyte.workers.temporal.TemporalJobType;
import io.temporal.failure.TemporalException;
import java.nio.file.Path;

public class TemporalWorkerRunFactory {

  private final TemporalClient temporalClient;
  private final Path workspaceRoot;

  public TemporalWorkerRunFactory(TemporalClient temporalClient, Path workspaceRoot) {
    this.temporalClient = temporalClient;
    this.workspaceRoot = workspaceRoot;
  }

  public WorkerRun create(Job job) {
    final int attemptId = job.getAttemptsCount();
    return WorkerRun.create(workspaceRoot, job.getId(), attemptId, createSupplier(job, attemptId));
  }

  // suppress "CodeBlock2Expr" because in the lambda syntax without a return statement the formatting
  // makes the switch statement very hard to read.
  @SuppressWarnings({"CodeBlock2Expr"})
  public CheckedSupplier<OutputAndStatus<JobOutput>, Exception> createSupplier(Job job, int attemptId) {
    final TemporalJobType temporalJobType = toTemporalJobType(job.getConfigType());
    return switch (job.getConfigType()) {
      case SYNC -> () -> {
        return toOutputAndStatus(() -> {
          final StandardSyncOutput output = temporalClient.submitSync(job.getId(), attemptId, job.getConfig().getSync());
          return new JobOutput().withSync(output);
        });
      };
      case RESET_CONNECTION -> () -> {
        return toOutputAndStatus(() -> {
          final JobResetConnectionConfig resetConnection = job.getConfig().getResetConnection();
          final JobSyncConfig config = new JobSyncConfig()
              .withPrefix(resetConnection.getPrefix())
              .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
              .withDestinationDockerImage(resetConnection.getDestinationDockerImage())
              .withSourceConfiguration(Jsons.emptyObject())
              .withDestinationConfiguration(resetConnection.getDestinationConfiguration())
              .withConfiguredAirbyteCatalog(resetConnection.getConfiguredAirbyteCatalog());

          final StandardSyncOutput output = temporalClient.submitSync(job.getId(), attemptId, config);
          return new JobOutput().withSync(output);
        });
      };
      default -> throw new IllegalArgumentException("Does not support job type: " + temporalJobType);
    };
  }

  private static TemporalJobType toTemporalJobType(ConfigType jobType) {
    return switch (jobType) {
      case GET_SPEC -> TemporalJobType.GET_SPEC;
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION -> TemporalJobType.CHECK_CONNECTION;
      case DISCOVER_SCHEMA -> TemporalJobType.DISCOVER_SCHEMA;
      case SYNC, RESET_CONNECTION -> TemporalJobType.SYNC;
    };
  }

  private OutputAndStatus<JobOutput> toOutputAndStatus(CheckedSupplier<JobOutput, TemporalJobException> supplier) {
    try {
      return new OutputAndStatus<>(JobStatus.SUCCEEDED, supplier.get());
    } catch (TemporalJobException | TemporalException e) {
      // while from within the temporal activity we throw TemporalJobException, Temporal wraps any
      // exception thrown by an activity in an ApplicationFailure exception, which gets wrapped in
      // ActivityFailure exception which get wrapped in a WorkflowFailedException. We will need to unwrap
      // these later, but for now we just catch the parent.
      return new OutputAndStatus<>(JobStatus.FAILED);
    }
  }

}
