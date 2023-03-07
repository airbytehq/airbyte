/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.run;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import java.nio.file.Path;
import java.util.UUID;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@AllArgsConstructor
public class TemporalWorkerRunFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalWorkerRunFactory.class);

  private final TemporalClient temporalClient;
  private final Path workspaceRoot;
  private final String airbyteVersionOrWarnings;
  private final FeatureFlags featureFlags;

  public WorkerRun create(final Job job) {
    final int attemptId = job.getAttemptsCount();
    return WorkerRun.create(workspaceRoot, job.getId(), attemptId, createSupplier(job, attemptId), airbyteVersionOrWarnings);
  }

  public CheckedSupplier<OutputAndStatus<JobOutput>, Exception> createSupplier(final Job job, final int attemptId) {
    final TemporalJobType temporalJobType = toTemporalJobType(job.getConfigType());
    final UUID connectionId = UUID.fromString(job.getScope());
    return switch (job.getConfigType()) {
      case SYNC -> () -> {
        final TemporalResponse<StandardSyncOutput> output = temporalClient.submitSync(job.getId(),
            attemptId, job.getConfig().getSync(), connectionId);
        return toOutputAndStatus(output);
      };
      case RESET_CONNECTION -> () -> {
        final JobResetConnectionConfig resetConnection = job.getConfig().getResetConnection();
        final JobSyncConfig config = new JobSyncConfig()
            .withNamespaceDefinition(resetConnection.getNamespaceDefinition())
            .withNamespaceFormat(resetConnection.getNamespaceFormat())
            .withPrefix(resetConnection.getPrefix())
            .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
            .withDestinationDockerImage(resetConnection.getDestinationDockerImage())
            .withDestinationProtocolVersion(resetConnection.getDestinationProtocolVersion())
            .withSourceConfiguration(Jsons.emptyObject())
            .withDestinationConfiguration(resetConnection.getDestinationConfiguration())
            .withConfiguredAirbyteCatalog(resetConnection.getConfiguredAirbyteCatalog())
            .withOperationSequence(resetConnection.getOperationSequence())
            .withResourceRequirements(resetConnection.getResourceRequirements())
            .withSourceResourceRequirements(resetConnection.getResourceRequirements())
            .withDestinationResourceRequirements(resetConnection.getResourceRequirements())
            .withIsSourceCustomConnector(false)
            .withIsDestinationCustomConnector(resetConnection.getIsDestinationCustomConnector());

        final TemporalResponse<StandardSyncOutput> output = temporalClient.submitSync(job.getId(), attemptId, config, connectionId);
        return toOutputAndStatus(output);
      };
      default -> throw new IllegalArgumentException("Does not support job type: " + temporalJobType);
    };
  }

  private static TemporalJobType toTemporalJobType(final ConfigType jobType) {
    return switch (jobType) {
      case GET_SPEC -> TemporalJobType.GET_SPEC;
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION -> TemporalJobType.CHECK_CONNECTION;
      case DISCOVER_SCHEMA -> TemporalJobType.DISCOVER_SCHEMA;
      case SYNC, RESET_CONNECTION -> TemporalJobType.SYNC;
    };
  }

  private OutputAndStatus<JobOutput> toOutputAndStatus(final TemporalResponse<StandardSyncOutput> response) {
    final JobStatus status;
    if (!response.isSuccess()) {
      status = JobStatus.FAILED;
    } else {
      final ReplicationStatus replicationStatus = response.getOutput().orElseThrow().getStandardSyncSummary().getStatus();
      if (replicationStatus == ReplicationStatus.FAILED || replicationStatus == ReplicationStatus.CANCELLED) {
        status = JobStatus.FAILED;
      } else {
        status = JobStatus.SUCCEEDED;
      }
    }
    return new OutputAndStatus<>(status, new JobOutput().withSync(response.getOutput().orElse(null)));
  }

}
