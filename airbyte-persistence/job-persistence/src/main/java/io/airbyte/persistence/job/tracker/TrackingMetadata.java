/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.tracker;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobOutput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.ScheduleData;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.Job;
import java.util.Collection;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.util.Strings;

public class TrackingMetadata {

  public static Map<String, Object> generateSyncMetadata(final StandardSync standardSync) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", standardSync.getConnectionId());

    final String frequencyString;
    if (standardSync.getScheduleType() != null) {
      frequencyString = getFrequencyStringFromScheduleType(standardSync.getScheduleType(), standardSync.getScheduleData());
    } else if (standardSync.getManual()) {
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

  public static Map<String, Object> generateDestinationDefinitionMetadata(final StandardDestinationDefinition destinationDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_destination", destinationDefinition.getName());
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
    metadata.put("connector_destination_docker_repository", destinationDefinition.getDockerRepository());
    final String imageTag = destinationDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_destination_version", imageTag);
    }
    return metadata.build();
  }

  public static Map<String, Object> generateSourceDefinitionMetadata(final StandardSourceDefinition sourceDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_source", sourceDefinition.getName());
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    metadata.put("connector_source_docker_repository", sourceDefinition.getDockerRepository());
    final String imageTag = sourceDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_source_version", imageTag);
    }
    return metadata.build();
  }

  public static Map<String, Object> generateJobAttemptMetadata(final Job job) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    if (job != null) {
      final List<Attempt> attempts = job.getAttempts();
      if (attempts != null && !attempts.isEmpty()) {
        final Attempt lastAttempt = attempts.get(attempts.size() - 1);
        if (lastAttempt.getOutput() != null && lastAttempt.getOutput().isPresent()) {
          final JobOutput jobOutput = lastAttempt.getOutput().get();
          if (jobOutput.getSync() != null) {
            final StandardSyncSummary syncSummary = jobOutput.getSync().getStandardSyncSummary();
            final SyncStats totalStats = syncSummary.getTotalStats();
            final NormalizationSummary normalizationSummary = jobOutput.getSync().getNormalizationSummary();

            if (syncSummary.getStartTime() != null)
              metadata.put("sync_start_time", syncSummary.getStartTime());
            if (syncSummary.getEndTime() != null && syncSummary.getStartTime() != null)
              metadata.put("duration", Math.round((syncSummary.getEndTime() - syncSummary.getStartTime()) / 1000.0));
            if (syncSummary.getBytesSynced() != null)
              metadata.put("volume_mb", syncSummary.getBytesSynced());
            if (syncSummary.getRecordsSynced() != null)
              metadata.put("volume_rows", syncSummary.getRecordsSynced());
            if (totalStats.getSourceStateMessagesEmitted() != null)
              metadata.put("count_state_messages_from_source", syncSummary.getTotalStats().getSourceStateMessagesEmitted());
            if (totalStats.getDestinationStateMessagesEmitted() != null)
              metadata.put("count_state_messages_from_destination", syncSummary.getTotalStats().getDestinationStateMessagesEmitted());
            if (totalStats.getMaxSecondsBeforeSourceStateMessageEmitted() != null)
              metadata.put("max_seconds_before_source_state_message_emitted",
                  totalStats.getMaxSecondsBeforeSourceStateMessageEmitted());
            if (totalStats.getMeanSecondsBeforeSourceStateMessageEmitted() != null)
              metadata.put("mean_seconds_before_source_state_message_emitted",
                  totalStats.getMeanSecondsBeforeSourceStateMessageEmitted());
            if (totalStats.getMaxSecondsBetweenStateMessageEmittedandCommitted() != null)
              metadata.put("max_seconds_between_state_message_emit_and_commit",
                  totalStats.getMaxSecondsBetweenStateMessageEmittedandCommitted());
            if (totalStats.getMeanSecondsBetweenStateMessageEmittedandCommitted() != null)
              metadata.put("mean_seconds_between_state_message_emit_and_commit",
                  totalStats.getMeanSecondsBetweenStateMessageEmittedandCommitted());

            if (totalStats.getReplicationStartTime() != null)
              metadata.put("replication_start_time", totalStats.getReplicationStartTime());
            if (totalStats.getReplicationEndTime() != null)
              metadata.put("replication_end_time", totalStats.getReplicationEndTime());
            if (totalStats.getSourceReadStartTime() != null)
              metadata.put("source_read_start_time", totalStats.getSourceReadStartTime());
            if (totalStats.getSourceReadEndTime() != null)
              metadata.put("source_read_end_time", totalStats.getSourceReadEndTime());
            if (totalStats.getDestinationWriteStartTime() != null)
              metadata.put("destination_write_start_time", totalStats.getDestinationWriteStartTime());
            if (totalStats.getDestinationWriteEndTime() != null)
              metadata.put("destination_write_end_time", totalStats.getDestinationWriteEndTime());

            if (normalizationSummary != null) {
              if (normalizationSummary.getStartTime() != null)
                metadata.put("normalization_start_time", normalizationSummary.getStartTime());
              if (normalizationSummary.getEndTime() != null)
                metadata.put("normalization_end_time", normalizationSummary.getEndTime());
            }
          }
        }

        final List<FailureReason> failureReasons = failureReasonsList(attempts);
        if (!failureReasons.isEmpty()) {
          metadata.put("failure_reasons", failureReasonsListAsJson(failureReasons).toString());
          metadata.put("main_failure_reason", failureReasonAsJson(failureReasons.get(0)).toString());
        }
      }
    }
    return metadata.build();
  }

  private static List<FailureReason> failureReasonsList(final List<Attempt> attempts) {
    return attempts
        .stream()
        .map(Attempt::getFailureSummary)
        .flatMap(Optional::stream)
        .map(AttemptFailureSummary::getFailures)
        .flatMap(Collection::stream)
        .sorted(Comparator.comparing(FailureReason::getTimestamp))
        .toList();
  }

  private static ArrayNode failureReasonsListAsJson(final List<FailureReason> failureReasons) {
    return Jsons.arrayNode().addAll(failureReasons
        .stream()
        .map(TrackingMetadata::failureReasonAsJson)
        .toList());
  }

  private static JsonNode failureReasonAsJson(final FailureReason failureReason) {
    // we want the json to always include failureOrigin and failureType, even when they are null
    final LinkedHashMap<String, Object> linkedHashMap = new LinkedHashMap<>();
    linkedHashMap.put("failureOrigin", failureReason.getFailureOrigin());
    linkedHashMap.put("failureType", failureReason.getFailureType());
    linkedHashMap.put("internalMessage", failureReason.getInternalMessage());
    linkedHashMap.put("externalMessage", failureReason.getExternalMessage());
    linkedHashMap.put("metadata", failureReason.getMetadata());
    linkedHashMap.put("retryable", failureReason.getRetryable());
    linkedHashMap.put("timestamp", failureReason.getTimestamp());

    return Jsons.jsonNode(linkedHashMap);
  }

  private static String getFrequencyStringFromScheduleType(final ScheduleType scheduleType, final ScheduleData scheduleData) {
    switch (scheduleType) {
      case MANUAL -> {
        return "manual";
      }
      case BASIC_SCHEDULE -> {
        return TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(scheduleData.getBasicSchedule())) + " min";
      }
      case CRON -> {
        // TODO(https://github.com/airbytehq/airbyte/issues/2170): consider something more detailed.
        return "cron";
      }
      default -> {
        throw new RuntimeException("Unexpected schedule type");
      }
    }
  }

}
