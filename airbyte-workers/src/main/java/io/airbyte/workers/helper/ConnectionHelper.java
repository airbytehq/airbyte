/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConfigs;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class ConnectionHelper {

  private final ConfigRepository configRepository;
  private final WorkspaceHelper workspaceHelper;
  private final WorkerConfigs workerConfigs;

  public void deleteConnection(final UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConnectionRead connectionRead = buildConnectionRead(connectionId);

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .connectionId(connectionRead.getConnectionId())
        .operationIds(connectionRead.getOperationIds())
        .syncCatalog(connectionRead.getSyncCatalog())
        .schedule(connectionRead.getSchedule())
        .status(ConnectionStatus.DEPRECATED)
        .resourceRequirements(connectionRead.getResourceRequirements());

    updateConnection(connectionUpdate);
  }

  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // retrieve and update sync
    // retrieve and update sync
    final StandardSync persistedSync = configRepository.getStandardSync(connectionUpdate.getConnectionId());

    validateWorkspace(persistedSync.getSourceId(), persistedSync.getDestinationId(), new HashSet<>(connectionUpdate.getOperationIds()));

    final StandardSync newConnection = Jsons.clone(persistedSync)
        .withNamespaceDefinition(Enums.convertTo(connectionUpdate.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(connectionUpdate.getNamespaceFormat())
        .withPrefix(connectionUpdate.getPrefix())
        .withOperationIds(connectionUpdate.getOperationIds())
        .withCatalog(CatalogConverter.toProtocol(connectionUpdate.getSyncCatalog()))
        .withStatus(toPersistenceStatus(connectionUpdate.getStatus()));

    // update Resource Requirements
    if (connectionUpdate.getResourceRequirements() != null) {
      newConnection.withResourceRequirements(new io.airbyte.config.ResourceRequirements()
          .withCpuRequest(connectionUpdate.getResourceRequirements().getCpuRequest())
          .withCpuLimit(connectionUpdate.getResourceRequirements().getCpuLimit())
          .withMemoryRequest(connectionUpdate.getResourceRequirements().getMemoryRequest())
          .withMemoryLimit(connectionUpdate.getResourceRequirements().getMemoryLimit()));
    } else {
      newConnection.withResourceRequirements(workerConfigs.getResourceRequirements());
    }

    // update sync schedule
    if (connectionUpdate.getSchedule() != null) {
      final Schedule newSchedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(connectionUpdate.getSchedule().getTimeUnit()))
          .withUnits(connectionUpdate.getSchedule().getUnits());
      newConnection.withManual(false).withSchedule(newSchedule);
    } else {
      newConnection.withManual(true).withSchedule(null);
    }

    configRepository.writeStandardSync(newConnection);
    return buildConnectionRead(connectionUpdate.getConnectionId());
  }

  public ConnectionRead buildConnectionRead(final UUID connectionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    return buildConnectionRead(standardSync);
  }

  public void validateWorkspace(final UUID sourceId, final UUID destinationId, final Set<UUID> operationIds) {
    final UUID sourceWorkspace = workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceId);
    final UUID destinationWorkspace = workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId);

    Preconditions.checkArgument(
        sourceWorkspace.equals(destinationWorkspace),
        String.format(
            "Source and destination do not belong to the same workspace. Source id: %s, Source workspace id: %s, Destination id: %s, Destination workspace id: %s",
            sourceId,
            sourceWorkspace,
            destinationId,
            destinationWorkspace));

    for (final UUID operationId : operationIds) {
      final UUID operationWorkspace = workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId);
      Preconditions.checkArgument(
          sourceWorkspace.equals(operationWorkspace),
          String.format(
              "Operation and connection do not belong to the same workspace. Workspace id: %s, Operation id: %s, Operation workspace id: %s",
              sourceWorkspace,
              operationId,
              operationWorkspace));
    }
  }

  private ConnectionRead buildConnectionRead(final StandardSync standardSync) {
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
      connectionRead.resourceRequirements(new ResourceRequirements()
          .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
          .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
          .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
          .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));
    } else {
      final io.airbyte.config.ResourceRequirements resourceRequirements = workerConfigs.getResourceRequirements();
      connectionRead.resourceRequirements(new ResourceRequirements()
          .cpuRequest(resourceRequirements.getCpuRequest())
          .cpuLimit(resourceRequirements.getCpuLimit())
          .memoryRequest(resourceRequirements.getMemoryRequest())
          .memoryLimit(resourceRequirements.getMemoryLimit()));
    }
    return connectionRead;
  }

  private ConnectionSchedule.TimeUnitEnum toApiTimeUnit(final Schedule.TimeUnit apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, ConnectionSchedule.TimeUnitEnum.class);
  }

  private ConnectionStatus toApiStatus(final StandardSync.Status status) {
    return Enums.convertTo(status, ConnectionStatus.class);
  }

  private StandardSync.Status toPersistenceStatus(final ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  private Schedule.TimeUnit toPersistenceTimeUnit(final ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, Schedule.TimeUnit.class);
  }

}
