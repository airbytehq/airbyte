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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.temporal.JobWorkflow;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConstants;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class JobSubmitter implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final JobPersistence persistence;
  private final ConfigRepository configRepository;
  private final JobWorkflow jobWorkflow;

  public JobSubmitter(final ExecutorService threadPool,
                      final JobPersistence persistence,
                      final ConfigRepository configRepository,
                      final JobWorkflow jobWorkflow) {
    this.threadPool = threadPool;
    this.persistence = persistence;
    this.configRepository = configRepository;
    this.jobWorkflow = jobWorkflow;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      final Optional<Job> nextJob = persistence.getNextJob();

      nextJob.ifPresent(job -> {
        trackSubmission(job);
        submitJob(job);
        LOGGER.info("Job-Submitter Summary. Submitted job with scope {}", job.getScope());
      });

      LOGGER.info("Completed Job-Submitter...");
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  @VisibleForTesting
  public void submitJob(Job job) {
    jobWorkflow.run(job);
  }

  @VisibleForTesting
  void trackSubmission(Job job) {
    try {
      // if there is no scope, do not track. this is the case where we are running check for sources /
      // destinations that don't exist.
      if (Strings.isNullOrEmpty(job.getScope())) {
        return;
      }
      final Builder<String, Object> metadataBuilder = generateMetadata(job);
      metadataBuilder.put("attempt_stage", "STARTED");
      track(metadataBuilder.build());
    } catch (Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
  }

  @VisibleForTesting
  void trackCompletion(Job job, io.airbyte.workers.JobStatus status) {
    try {
      // if there is no scope, do not track. this is the case where we are running check for sources /
      // destinations that don't exist.
      if (Strings.isNullOrEmpty(job.getScope())) {
        return;
      }
      final Builder<String, Object> metadataBuilder = generateMetadata(job);
      metadataBuilder.put("attempt_stage", "ENDED");
      metadataBuilder.put("attempt_completion_status", status);
      track(metadataBuilder.build());
    } catch (Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
  }

  private void track(Map<String, Object> metadata) {
    // do not track get spec. it is done frequently and not terribly interesting.
    if (metadata.get("job_type").equals("GET_SPEC")) {
      return;
    }

    TrackingClientSingleton.get().track("Connector Jobs", metadata);
  }

  private ImmutableMap.Builder<String, Object> generateMetadata(Job job) throws ConfigNotFoundException, IOException, JsonValidationException {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("job_type", job.getConfig().getConfigType());
    metadata.put("job_id", job.getId());
    metadata.put("attempt_id", job.getAttempts());
    // build deterministic job and attempt uuids based off of the scope,which should be unique across
    // all instances of airbyte installed everywhere).
    final UUID jobUuid = UUID.nameUUIDFromBytes((job.getScope() + job.getId() + job.getAttempts()).getBytes(Charsets.UTF_8));
    final UUID attemptUuid = UUID.nameUUIDFromBytes((job.getScope() + job.getId() + job.getAttempts()).getBytes(Charsets.UTF_8));
    metadata.put("job_uuid", jobUuid);
    metadata.put("attempt_uuid", attemptUuid);

    switch (job.getConfig().getConfigType()) {
      case CHECK_CONNECTION_SOURCE, DISCOVER_SCHEMA -> {
        final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromSource(UUID.fromString(job.getScope()));

        metadata.put("connector_source", sourceDefinition.getName());
        metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
      }
      case CHECK_CONNECTION_DESTINATION -> {
        final StandardDestinationDefinition destinationDefinition = configRepository
            .getDestinationDefinitionFromDestination(UUID.fromString(job.getScope()));

        metadata.put("connector_destination", destinationDefinition.getName());
        metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
      }
      case GET_SPEC -> {
        // no op because this will be noisy as heck.
      }
      case SYNC -> {
        final UUID connectionId = UUID.fromString(job.getScope());
        final StandardSyncSchedule schedule = configRepository.getStandardSyncSchedule(connectionId);
        final StandardSourceDefinition sourceDefinition = configRepository
            .getSourceDefinitionFromConnection(connectionId);
        final StandardDestinationDefinition destinationDefinition = configRepository
            .getDestinationDefinitionFromConnection(connectionId);

        metadata.put("connection_id", connectionId);
        metadata.put("connector_source", sourceDefinition.getName());
        metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
        metadata.put("connector_destination", destinationDefinition.getName());
        metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());

        String frequencyString;
        if (schedule.getManual()) {
          frequencyString = "manual";
        } else {
          final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(schedule.getSchedule()));
          frequencyString = intervalInMinutes + " min";
        }
        metadata.put("frequency", frequencyString);
      }
    }
    return metadata;
  }

}
