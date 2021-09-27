/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_tracker;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.config.JobOutput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.util.Strings;

public class TrackingMetadata {

  public static ImmutableMap<String, Object> generateSyncMetadata(StandardSync standardSync) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", standardSync.getConnectionId());

    final String frequencyString;
    if (standardSync.getManual()) {
      frequencyString = "manual";
    } else {
      final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule()));
      frequencyString = intervalInMinutes + " min";
    }
    metadata.put("frequency", frequencyString);

    final int operationCount = standardSync.getOperationIds() != null ? standardSync.getOperationIds().size() : 0;
    metadata.put("operation_count", operationCount);
    if (standardSync.getNamespaceDefinition() != null) {
      metadata.put("namespace_definition", standardSync.getNamespaceDefinition());
    }

    final boolean isUsingPrefix = standardSync.getPrefix() != null && !standardSync.getPrefix().isBlank();
    metadata.put("table_prefix", isUsingPrefix);

    final ResourceRequirements resourceRequirements = standardSync.getResourceRequirements();

    if (resourceRequirements != null) {
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getCpuRequest())) {
        metadata.put("sync_cpu_request", resourceRequirements.getCpuRequest());
      }
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getCpuLimit())) {
        metadata.put("sync_cpu_limit", resourceRequirements.getCpuLimit());
      }
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getMemoryRequest())) {
        metadata.put("sync_memory_request", resourceRequirements.getMemoryRequest());
      }
      if (!com.google.common.base.Strings.isNullOrEmpty(resourceRequirements.getMemoryLimit())) {
        metadata.put("sync_memory_limit", resourceRequirements.getMemoryLimit());
      }
    }
    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateDestinationDefinitionMetadata(StandardDestinationDefinition destinationDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_destination", destinationDefinition.getName());
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
    final String imageTag = destinationDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_destination_version", imageTag);
    }
    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateSourceDefinitionMetadata(StandardSourceDefinition sourceDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_source", sourceDefinition.getName());
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    final String imageTag = sourceDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_source_version", imageTag);
    }
    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateJobAttemptMetadata(Job job) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    if (job != null) {
      final List<Attempt> attempts = job.getAttempts();
      if (attempts != null && !attempts.isEmpty()) {
        final Attempt lastAttempt = attempts.get(attempts.size() - 1);
        if (lastAttempt.getOutput() != null && lastAttempt.getOutput().isPresent()) {
          final JobOutput jobOutput = lastAttempt.getOutput().get();
          if (jobOutput.getSync() != null) {
            final StandardSyncSummary syncSummary = jobOutput.getSync().getStandardSyncSummary();
            metadata.put("duration", Math.round((syncSummary.getEndTime() - syncSummary.getStartTime()) / 1000.0));
            metadata.put("volume_mb", syncSummary.getBytesSynced());
            metadata.put("volume_rows", syncSummary.getRecordsSynced());
          }
        }
      }
    }
    return metadata.build();
  }

}
