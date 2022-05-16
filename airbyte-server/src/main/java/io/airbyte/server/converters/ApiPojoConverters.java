/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.ActorDefinitionResourceRequirements;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.JobType;
import io.airbyte.api.model.JobTypeResourceLimit;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.server.handlers.helpers.CatalogConverter;
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

  public static io.airbyte.config.StandardSync connectionUpdateToInternal(final ConnectionUpdate update) {

    final StandardSync newConnection = new StandardSync()
        .withNamespaceDefinition(Enums.convertTo(update.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(update.getNamespaceFormat())
        .withPrefix(update.getPrefix())
        .withOperationIds(update.getOperationIds())
        .withCatalog(CatalogConverter.toProtocol(update.getSyncCatalog()))
        .withStatus(toPersistenceStatus(update.getStatus()))
        .withSourceCatalogId(update.getSourceCatalogId());

    if (update.getName() != null) {
      newConnection.withName(update.getName());
    }

    // update Resource Requirements
    if (update.getResourceRequirements() != null) {
      newConnection.withResourceRequirements(resourceRequirementsToInternal(update.getResourceRequirements()));
    }

    // update sync schedule
    if (update.getSchedule() != null) {
      final Schedule newSchedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(update.getSchedule().getTimeUnit()))
          .withUnits(update.getSchedule().getUnits());
      newConnection.withManual(false).withSchedule(newSchedule);
    } else {
      newConnection.withManual(true).withSchedule(null);
    }

    return newConnection;
  }

  public static ConnectionRead internalToConnectionRead(final StandardSync standardSync) {
    ConnectionSchedule apiSchedule = null;

    if (!standardSync.getManual()) {
      apiSchedule = new ConnectionSchedule()
          .timeUnit(toApiTimeUnit(standardSync.getSchedule().getTimeUnit()))
          .units(standardSync.getSchedule().getUnits());
    }

    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(standardSync.getConnectionId())
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .status(toApiStatus(standardSync.getStatus()))
        .schedule(apiSchedule)
        .name(standardSync.getName())
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), io.airbyte.api.model.NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .syncCatalog(CatalogConverter.toApi(standardSync.getCatalog()));

    if (standardSync.getResourceRequirements() != null) {
      connectionRead.resourceRequirements(resourceRequirementsToApi(standardSync.getResourceRequirements()));
    }

    return connectionRead;
  }

  public static JobType toApiJobType(final io.airbyte.config.JobTypeResourceLimit.JobType jobType) {
    return Enums.convertTo(jobType, JobType.class);
  }

  public static io.airbyte.config.JobTypeResourceLimit.JobType toInternalJobType(final JobType jobType) {
    return Enums.convertTo(jobType, io.airbyte.config.JobTypeResourceLimit.JobType.class);
  }

  public static ConnectionSchedule.TimeUnitEnum toApiTimeUnit(final Schedule.TimeUnit apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, ConnectionSchedule.TimeUnitEnum.class);
  }

  public static ConnectionStatus toApiStatus(final StandardSync.Status status) {
    return Enums.convertTo(status, ConnectionStatus.class);
  }

  public static StandardSync.Status toPersistenceStatus(final ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  public static Schedule.TimeUnit toPersistenceTimeUnit(final ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, Schedule.TimeUnit.class);
  }

}
