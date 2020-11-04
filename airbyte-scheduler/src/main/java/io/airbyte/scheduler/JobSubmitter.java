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

package io.airbyte.scheduler;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class JobSubmitter implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final SchedulerPersistence persistence;
  private final ConfigRepository configRepository;
  private final WorkerRunFactory workerRunFactory;

  public JobSubmitter(final ExecutorService threadPool,
                      final SchedulerPersistence persistence,
                      final ConfigRepository configRepository,
                      final WorkerRunFactory workerRunFactory) {
    this.threadPool = threadPool;
    this.persistence = persistence;
    this.configRepository = configRepository;
    this.workerRunFactory = workerRunFactory;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      Optional<Job> oldestPendingJob = persistence.getOldestPendingJob();

      oldestPendingJob.ifPresent(job -> {
        track(job, configRepository);
        submitJob(job);
      });

      LOGGER.info("Completed job-submitter...");
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  private void submitJob(Job job) {
    final WorkerRun workerRun = workerRunFactory.create(job);
    threadPool.submit(new LifecycledCallable.Builder<>(workerRun)
        .setOnStart(() -> {
          persistence.updateStatus(job.getId(), JobStatus.RUNNING);
          final Path logFilePath = workerRun.getJobRoot().resolve(WorkerConstants.LOG_FILENAME);
          persistence.updateLogPath(job.getId(), logFilePath);
          persistence.incrementAttempts(job.getId());
          MDC.put("job_id", String.valueOf(job.getId()));
          MDC.put("job_root", logFilePath.getParent().toString());
          MDC.put("job_log_filename", logFilePath.getFileName().toString());
        })
        .setOnSuccess(output -> {
          if (output.getOutput().isPresent()) {
            persistence.writeOutput(job.getId(), output.getOutput().get());
          }
          persistence.updateStatus(job.getId(), getStatus(output));
        })
        .setOnException(noop -> persistence.updateStatus(job.getId(), JobStatus.FAILED))
        .setOnFinish(MDC::clear)
        .build());
  }

  private void track(Job job, ConfigRepository configRepository) {
    try {
      final Builder<String, Object> metadata = ImmutableMap.builder();
      switch (job.getConfig().getConfigType()) {
        case CHECK_CONNECTION_SOURCE, DISCOVER_SCHEMA -> {
          final StandardSourceDefinition sourceDefinition = configRepository
              .getSourceDefinitionFromSource(UUID.fromString(ScopeHelper.getConfigId(job.getScope())));

          metadata.put("source_definition_name", sourceDefinition.getName());
          metadata.put("source_definition_id", sourceDefinition.getSourceDefinitionId());
        }
        case CHECK_CONNECTION_DESTINATION -> {
          final StandardDestinationDefinition destinationDefinition = configRepository
              .getDestinationDefinitionFromDestination(UUID.fromString(ScopeHelper.getConfigId(job.getScope())));

          metadata.put("destination_definition_name", destinationDefinition.getName());
          metadata.put("destination_definition_id", destinationDefinition.getDestinationDefinitionId());
        }
        case GET_SPEC -> {
          // no op because this will be noisy as heck.
        }
        case SYNC -> {
          final StandardSourceDefinition sourceDefinition = configRepository
              .getSourceDefinitionFromConnection(UUID.fromString(ScopeHelper.getConfigId(job.getScope())));
          final StandardDestinationDefinition destinationDefinition = configRepository
              .getDestinationDefinitionFromConnection(UUID.fromString(ScopeHelper.getConfigId(job.getScope())));

          metadata.put("source_definition_name", sourceDefinition.getName());
          metadata.put("source_definition_id", sourceDefinition.getSourceDefinitionId());
          metadata.put("destination_definition_name", destinationDefinition.getName());
          metadata.put("destination_definition_id", destinationDefinition.getDestinationDefinitionId());
        }
      }

      TrackingClientSingleton.get().track("job", metadata.build());
    } catch (Exception e) {
      LOGGER.error("failed while reporting usage.");
    }
  }

  private JobStatus getStatus(OutputAndStatus<?> output) {
    switch (output.getStatus()) {
      case SUCCEEDED:
        return JobStatus.COMPLETED;
      case FAILED:
        return JobStatus.FAILED;
      default:
        throw new RuntimeException("Unknown state " + output.getStatus());
    }
  }

}
