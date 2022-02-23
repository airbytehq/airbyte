/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.workers.helper.CatalogConverter;

public class ApiPojoConverters {

  public static io.airbyte.config.ResourceRequirements resourceRequirementsToInternal(final ResourceRequirements resourceRequirements) {
    return new io.airbyte.config.ResourceRequirements()
        .withCpuRequest(resourceRequirements.getCpuRequest())
        .withCpuLimit(resourceRequirements.getCpuLimit())
        .withMemoryRequest(resourceRequirements.getMemoryRequest())
        .withMemoryLimit(resourceRequirements.getMemoryLimit());
  }

  public static ResourceRequirements resourceRequirementsToApi(final io.airbyte.config.ResourceRequirements resourceRequirements) {
    return new ResourceRequirements()
        .cpuRequest(resourceRequirements.getCpuRequest())
        .cpuLimit(resourceRequirements.getCpuLimit())
        .memoryRequest(resourceRequirements.getMemoryRequest())
        .memoryLimit(resourceRequirements.getMemoryLimit());
  }

  public static io.airbyte.config.StandardSync connectionUpdateToInternal(final ConnectionUpdate update) {

    final StandardSync newConnection = new StandardSync()
        .withNamespaceDefinition(Enums.convertTo(update.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(update.getNamespaceFormat())
        .withPrefix(update.getPrefix())
        .withOperationIds(update.getOperationIds())
        .withCatalog(CatalogConverter.toProtocol(update.getSyncCatalog()))
        .withStatus(toPersistenceStatus(update.getStatus()));

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
