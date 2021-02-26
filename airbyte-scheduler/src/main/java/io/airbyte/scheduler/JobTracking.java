package io.airbyte.scheduler;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobTracking {
  private static final Logger LOGGER = LoggerFactory.getLogger(JobTracking.class);

  private final ConfigRepository configRepository;

  public JobTracking(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
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
  void trackCompletion(Job job, JobStatus status) {
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

  private Builder<String, Object> generateMetadata(Job job) throws ConfigNotFoundException, IOException, JsonValidationException {
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
