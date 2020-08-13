package io.dataline.server.handlers;

import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.*;
import io.dataline.server.errors.KnownException;
import java.util.UUID;

public class WorkspacesHandler {
  private final ConfigPersistence configPersistence;

  public WorkspacesHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public WorkspaceRead getWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {
    return getWorkspaceFromId(workspaceIdRequestBody.getWorkspaceId());
  }

  @SuppressWarnings("unused")
  public WorkspaceRead getWorkspaceBySlug(SlugRequestBody slugRequestBody) {
    // for now we assume there is one workspace and it has a default uuid.
    return getWorkspaceFromId(WorkspaceConstants.DEFAULT_WORKSPACE_ID);
  }

  private WorkspaceRead getWorkspaceFromId(UUID workspaceIdUuid) {
    final String workspaceId = workspaceIdUuid.toString();
    final StandardWorkspace workspace;
    try {
      workspace =
          configPersistence.getConfig(
              PersistenceConfigType.STANDARD_WORKSPACE, workspaceId, StandardWorkspace.class);
    } catch (ConfigNotFoundException e) {
      throw new KnownException(404, e.getMessage(), e);
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    final WorkspaceRead workspaceRead = new WorkspaceRead();
    workspaceRead.setWorkspaceId(workspace.getWorkspaceId());
    workspaceRead.setName(workspace.getName());
    workspaceRead.setSlug(workspace.getSlug());
    workspaceRead.setInitialSetupComplete(workspace.getInitialSetupComplete());

    return workspaceRead;
  }

  public WorkspaceRead updateWorkspace(WorkspaceUpdate workspaceUpdate) {
    final String workspaceId = workspaceUpdate.getWorkspaceId().toString();

    final StandardWorkspace persistedWorkspace;
    try {
      persistedWorkspace =
          configPersistence.getConfig(
              PersistenceConfigType.STANDARD_WORKSPACE, workspaceId, StandardWorkspace.class);
    } catch (ConfigNotFoundException e) {
      throw new KnownException(404, e.getMessage(), e);
    } catch (JsonValidationException e) {
      throw new KnownException(422, e.getMessage(), e);
    }

    if (workspaceUpdate.getEmail() != null && !workspaceUpdate.getEmail().equals("")) {
      persistedWorkspace.setEmail(workspaceUpdate.getEmail());
    }
    persistedWorkspace.setInitialSetupComplete(workspaceUpdate.getInitialSetupComplete());
    persistedWorkspace.setAnonymousDataCollection(workspaceUpdate.getAnonymousDataCollection());
    persistedWorkspace.setNews(workspaceUpdate.getNews());
    persistedWorkspace.setSecurityUpdates(workspaceUpdate.getSecurityUpdates());
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_WORKSPACE, workspaceId, persistedWorkspace);

    return getWorkspaceFromId(workspaceUpdate.getWorkspaceId());
  }
}
