/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import io.airbyte.api.model.generated.ActorDefinitionResourceRequirements;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionSchedule;
import io.airbyte.api.model.generated.ConnectionScheduleData;
import io.airbyte.api.model.generated.ConnectionScheduleDataBasicSchedule;
import io.airbyte.api.model.generated.ConnectionScheduleDataCron;
import io.airbyte.api.model.generated.ConnectionStatus;
import io.airbyte.api.model.generated.Geography;
import io.airbyte.api.model.generated.JobType;
import io.airbyte.api.model.generated.JobTypeResourceLimit;
import io.airbyte.api.model.generated.NonBreakingChangesPreference;
import io.airbyte.api.model.generated.NormalizationDestinationDefinitionConfig;
import io.airbyte.api.model.generated.ResourceRequirements;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.server.handlers.helpers.CatalogConverter;
import io.airbyte.config.BasicSchedule;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import java.util.stream.Collectors;

public class ApiPojoConverters {

  public static io.airbyte.config.ActorDefinitionResourceRequirements actorDefResourceReqsToInternal(final ActorDefinitionResourceRequirements actorDefResourceReqs) {
    if (actorDefResourceReqs == null) {
      return null;
    }

    return new io.airbyte.config.ActorDefinitionResourceRequirements()
        .withDefault(actorDefResourceReqs.getDefault() == null ? null : resourceRequirementsToInternal(actorDefResourceReqs.getDefault()))
        .withJobSpecific(actorDefResourceReqs.getJobSpecific() == null ? null
            : actorDefResourceReqs.getJobSpecific()
                .stream()
                .map(jobSpecific -> new io.airbyte.config.JobTypeResourceLimit()
                    .withJobType(toInternalJobType(jobSpecific.getJobType()))
                    .withResourceRequirements(resourceRequirementsToInternal(jobSpecific.getResourceRequirements())))
                .collect(Collectors.toList()));
  }

  public static ActorDefinitionResourceRequirements actorDefResourceReqsToApi(final io.airbyte.config.ActorDefinitionResourceRequirements actorDefResourceReqs) {
    if (actorDefResourceReqs == null) {
      return null;
    }

    return new ActorDefinitionResourceRequirements()
        ._default(actorDefResourceReqs.getDefault() == null ? null : resourceRequirementsToApi(actorDefResourceReqs.getDefault()))
        .jobSpecific(actorDefResourceReqs.getJobSpecific() == null ? null
            : actorDefResourceReqs.getJobSpecific()
                .stream()
                .map(jobSpecific -> new JobTypeResourceLimit()
                    .jobType(toApiJobType(jobSpecific.getJobType()))
                    .resourceRequirements(resourceRequirementsToApi(jobSpecific.getResourceRequirements())))
                .collect(Collectors.toList()));
  }

  public static io.airbyte.config.ResourceRequirements resourceRequirementsToInternal(final ResourceRequirements resourceReqs) {
    if (resourceReqs == null) {
      return null;
    }

    return new io.airbyte.config.ResourceRequirements()
        .withCpuRequest(resourceReqs.getCpuRequest())
        .withCpuLimit(resourceReqs.getCpuLimit())
        .withMemoryRequest(resourceReqs.getMemoryRequest())
        .withMemoryLimit(resourceReqs.getMemoryLimit());
  }

  public static ResourceRequirements resourceRequirementsToApi(final io.airbyte.config.ResourceRequirements resourceReqs) {
    if (resourceReqs == null) {
      return null;
    }

    return new ResourceRequirements()
        .cpuRequest(resourceReqs.getCpuRequest())
        .cpuLimit(resourceReqs.getCpuLimit())
        .memoryRequest(resourceReqs.getMemoryRequest())
        .memoryLimit(resourceReqs.getMemoryLimit());
  }

  public static NormalizationDestinationDefinitionConfig normalizationDestinationDefinitionConfigToApi(final io.airbyte.config.NormalizationDestinationDefinitionConfig normalizationDestinationDefinitionConfig) {
    if (normalizationDestinationDefinitionConfig == null) {
      return new NormalizationDestinationDefinitionConfig().supported(false);
    }
    return new NormalizationDestinationDefinitionConfig()
        .supported(true)
        .normalizationRepository(normalizationDestinationDefinitionConfig.getNormalizationRepository())
        .normalizationTag(normalizationDestinationDefinitionConfig.getNormalizationTag())
        .normalizationIntegrationType(normalizationDestinationDefinitionConfig.getNormalizationIntegrationType());
  }

  public static ConnectionRead internalToConnectionRead(final StandardSync standardSync) {
    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(standardSync.getConnectionId())
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .status(toApiStatus(standardSync.getStatus()))
        .name(standardSync.getName())
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), io.airbyte.api.model.generated.NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .syncCatalog(CatalogConverter.toApi(standardSync.getCatalog(), standardSync.getFieldSelectionData()))
        .sourceCatalogId(standardSync.getSourceCatalogId())
        .breakingChange(standardSync.getBreakingChange())
        .geography(Enums.convertTo(standardSync.getGeography(), Geography.class))
        .nonBreakingChangesPreference(Enums.convertTo(standardSync.getNonBreakingChangesPreference(), NonBreakingChangesPreference.class))
        .notifySchemaChanges(standardSync.getNotifySchemaChanges());

    if (standardSync.getResourceRequirements() != null) {
      connectionRead.resourceRequirements(resourceRequirementsToApi(standardSync.getResourceRequirements()));
    }

    populateConnectionReadSchedule(standardSync, connectionRead);

    return connectionRead;
  }

  public static JobType toApiJobType(final io.airbyte.config.JobTypeResourceLimit.JobType jobType) {
    return Enums.convertTo(jobType, JobType.class);
  }

  public static io.airbyte.config.JobTypeResourceLimit.JobType toInternalJobType(final JobType jobType) {
    return Enums.convertTo(jobType, io.airbyte.config.JobTypeResourceLimit.JobType.class);
  }

  // TODO(https://github.com/airbytehq/airbyte/issues/11432): remove these helpers.
  public static ConnectionSchedule.TimeUnitEnum toApiTimeUnit(final Schedule.TimeUnit apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, ConnectionSchedule.TimeUnitEnum.class);
  }

  public static ConnectionSchedule.TimeUnitEnum toApiTimeUnit(final BasicSchedule.TimeUnit timeUnit) {
    return Enums.convertTo(timeUnit, ConnectionSchedule.TimeUnitEnum.class);
  }

  public static ConnectionStatus toApiStatus(final StandardSync.Status status) {
    return Enums.convertTo(status, ConnectionStatus.class);
  }

  public static StandardSync.Status toPersistenceStatus(final ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  public static StandardSync.NonBreakingChangesPreference toPersistenceNonBreakingChangesPreference(final NonBreakingChangesPreference preference) {
    return Enums.convertTo(preference, StandardSync.NonBreakingChangesPreference.class);
  }

  public static Geography toApiGeography(final io.airbyte.config.Geography geography) {
    return Enums.convertTo(geography, Geography.class);
  }

  public static io.airbyte.config.Geography toPersistenceGeography(final Geography apiGeography) {
    return Enums.convertTo(apiGeography, io.airbyte.config.Geography.class);
  }

  public static Schedule.TimeUnit toPersistenceTimeUnit(final ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, Schedule.TimeUnit.class);
  }

  public static BasicSchedule.TimeUnit toBasicScheduleTimeUnit(final ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, BasicSchedule.TimeUnit.class);
  }

  public static BasicSchedule.TimeUnit toBasicScheduleTimeUnit(final ConnectionScheduleDataBasicSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, BasicSchedule.TimeUnit.class);
  }

  public static Schedule.TimeUnit toLegacyScheduleTimeUnit(final ConnectionScheduleDataBasicSchedule.TimeUnitEnum timeUnit) {
    return Enums.convertTo(timeUnit, Schedule.TimeUnit.class);
  }

  public static ConnectionScheduleDataBasicSchedule.TimeUnitEnum toApiBasicScheduleTimeUnit(final BasicSchedule.TimeUnit timeUnit) {
    return Enums.convertTo(timeUnit, ConnectionScheduleDataBasicSchedule.TimeUnitEnum.class);
  }

  public static ConnectionScheduleDataBasicSchedule.TimeUnitEnum toApiBasicScheduleTimeUnit(final Schedule.TimeUnit timeUnit) {
    return Enums.convertTo(timeUnit, ConnectionScheduleDataBasicSchedule.TimeUnitEnum.class);
  }

  public static io.airbyte.api.model.generated.ConnectionScheduleType toApiConnectionScheduleType(final StandardSync standardSync) {
    if (standardSync.getScheduleType() != null) {
      switch (standardSync.getScheduleType()) {
        case MANUAL -> {
          return io.airbyte.api.model.generated.ConnectionScheduleType.MANUAL;
        }
        case BASIC_SCHEDULE -> {
          return io.airbyte.api.model.generated.ConnectionScheduleType.BASIC;
        }
        case CRON -> {
          return io.airbyte.api.model.generated.ConnectionScheduleType.CRON;
        }
        default -> throw new RuntimeException("Unexpected scheduleType " + standardSync.getScheduleType());
      }
    } else if (standardSync.getManual()) {
      // Legacy schema, manual sync.
      return io.airbyte.api.model.generated.ConnectionScheduleType.MANUAL;
    } else {
      // Legacy schema, basic schedule.
      return io.airbyte.api.model.generated.ConnectionScheduleType.BASIC;
    }
  }

  public static io.airbyte.api.model.generated.ConnectionScheduleData toApiConnectionScheduleData(final StandardSync standardSync) {
    if (standardSync.getScheduleType() != null) {
      switch (standardSync.getScheduleType()) {
        case MANUAL -> {
          return null;
        }
        case BASIC_SCHEDULE -> {
          return new ConnectionScheduleData()
              .basicSchedule(new ConnectionScheduleDataBasicSchedule()
                  .timeUnit(toApiBasicScheduleTimeUnit(standardSync.getScheduleData().getBasicSchedule().getTimeUnit()))
                  .units(standardSync.getScheduleData().getBasicSchedule().getUnits()));
        }
        case CRON -> {
          return new ConnectionScheduleData()
              .cron(new ConnectionScheduleDataCron()
                  .cronExpression(standardSync.getScheduleData().getCron().getCronExpression())
                  .cronTimeZone(standardSync.getScheduleData().getCron().getCronTimeZone()));
        }
        default -> throw new RuntimeException("Unexpected scheduleType " + standardSync.getScheduleType());
      }
    } else if (standardSync.getManual()) {
      // Legacy schema, manual sync.
      return null;
    } else {
      // Legacy schema, basic schedule.
      return new ConnectionScheduleData()
          .basicSchedule(new ConnectionScheduleDataBasicSchedule()
              .timeUnit(toApiBasicScheduleTimeUnit(standardSync.getSchedule().getTimeUnit()))
              .units(standardSync.getSchedule().getUnits()));
    }
  }

  public static ConnectionSchedule toLegacyConnectionSchedule(final StandardSync standardSync) {
    if (standardSync.getScheduleType() != null) {
      // Populate everything based on the new schema.
      switch (standardSync.getScheduleType()) {
        case MANUAL, CRON -> {
          // We don't populate any legacy data here.
          return null;
        }
        case BASIC_SCHEDULE -> {
          return new ConnectionSchedule()
              .timeUnit(toApiTimeUnit(standardSync.getScheduleData().getBasicSchedule().getTimeUnit()))
              .units(standardSync.getScheduleData().getBasicSchedule().getUnits());
        }
        default -> throw new RuntimeException("Unexpected scheduleType " + standardSync.getScheduleType());
      }
    } else if (standardSync.getManual()) {
      // Legacy schema, manual sync.
      return null;
    } else {
      // Legacy schema, basic schedule.
      return new ConnectionSchedule()
          .timeUnit(toApiTimeUnit(standardSync.getSchedule().getTimeUnit()))
          .units(standardSync.getSchedule().getUnits());
    }
  }

  public static void populateConnectionReadSchedule(final StandardSync standardSync, final ConnectionRead connectionRead) {
    connectionRead.scheduleType(toApiConnectionScheduleType(standardSync));
    connectionRead.scheduleData(toApiConnectionScheduleData(standardSync));

    // TODO(https://github.com/airbytehq/airbyte/issues/11432): only return new schema once frontend is
    // ready.
    connectionRead.schedule(toLegacyConnectionSchedule(standardSync));
  }

}
