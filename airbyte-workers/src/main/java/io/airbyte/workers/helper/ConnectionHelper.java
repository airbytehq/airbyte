/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.base.Preconditions;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import lombok.AllArgsConstructor;

// todo (cgardens) - we are not getting any value out of instantiating this class. we should just
// use it as statics. not doing it now, because already in the middle of another refactor.
@AllArgsConstructor
public class ConnectionHelper {

  private final ConfigRepository configRepository;
  private final WorkspaceHelper workspaceHelper;

  public void deleteConnection(final UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync update = Jsons.clone(configRepository.getStandardSync(connectionId).withStatus(StandardSync.Status.DEPRECATED));
    updateConnection(update);
  }

  /**
   * Given a connection update, fetches an existing connection, applies the update, and then persists
   * the update.
   *
   * @param update - updated sync info to be merged with original sync.
   * @return new sync object
   * @throws JsonValidationException - if provided object is invalid
   * @throws ConfigNotFoundException - if there is no sync already persisted
   * @throws IOException - you never know when you io
   */
  public StandardSync updateConnection(final StandardSync update)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync original = configRepository.getStandardSync(update.getConnectionId());
    final StandardSync newConnection = updateConnectionObject(workspaceHelper, original, update);
    configRepository.writeStandardSync(newConnection);
    return newConnection;
  }

  /**
   * Core logic for merging an existing connection configuration with an update.
   *
   * @param workspaceHelper - helper class
   * @param original - already persisted sync
   * @param update - updated sync info to be merged with original sync.
   * @return new sync object
   */
  public static StandardSync updateConnectionObject(final WorkspaceHelper workspaceHelper, final StandardSync original, final StandardSync update) {
    validateWorkspace(workspaceHelper, original.getSourceId(), original.getDestinationId(), new HashSet<>(update.getOperationIds()));

    final StandardSync newConnection = Jsons.clone(original)
        .withNamespaceDefinition(Enums.convertTo(update.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(update.getNamespaceFormat())
        .withPrefix(update.getPrefix())
        .withOperationIds(update.getOperationIds())
        .withCatalog(update.getCatalog())
        .withStatus(update.getStatus())
        .withSourceCatalogId(update.getSourceCatalogId());

    // update name
    if (update.getName() != null) {
      newConnection.withName(update.getName());
    }

    // update Resource Requirements
    if (update.getResourceRequirements() != null) {
      newConnection.withResourceRequirements(Jsons.clone(update.getResourceRequirements()));
    } else {
      newConnection.withResourceRequirements(original.getResourceRequirements());
    }

    // update sync schedule
    if (update.getSchedule() != null) {
      final Schedule newSchedule = new Schedule()
          .withTimeUnit(update.getSchedule().getTimeUnit())
          .withUnits(update.getSchedule().getUnits());
      newConnection.withManual(false).withSchedule(newSchedule);
    } else {
      newConnection.withManual(true).withSchedule(null);
    }

    return newConnection;
  }

  public static void validateWorkspace(final WorkspaceHelper workspaceHelper,
                                       final UUID sourceId,
                                       final UUID destinationId,
                                       final Set<UUID> operationIds) {
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

}
