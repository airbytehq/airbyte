package io.dataline.server.handlers;

import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.StandardWorkspaceConfiguration;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.config.persistence.WorkspaceConstants;
import java.util.UUID;

public class WorkspacesHandler {
  private final ConfigPersistence configPersistence;

  public WorkspacesHandler(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  public WorkspaceRead getWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {
    return getWorkspaceFromId(workspaceIdRequestBody.getWorkspaceId());
  }

  public WorkspaceRead getWorkspaceBySlug(SlugRequestBody slugRequestBody) {
    return getWorkspaceFromId(WorkspaceConstants.DEFAULT_WORKSPACE_ID);
  }

  private WorkspaceRead getWorkspaceFromId(UUID workspaceIdUuid) {
    final String workspaceId = workspaceIdUuid.toString();
    final StandardWorkspaceConfiguration workspace =
        configPersistence.getConfig(
            PersistenceConfigType.STANDARD_WORKSPACE_CONFIGURATION,
            workspaceId,
            StandardWorkspaceConfiguration.class);

    final WorkspaceRead workspaceRead = new WorkspaceRead();
    workspaceRead.setWorkspaceId(workspace.getWorkspaceId());
    workspaceRead.setName(workspace.getName());
    workspaceRead.setSlug(workspace.getSlug());
    workspaceRead.setInitialSetupComplete(workspace.getInitialSetupComplete());

    return workspaceRead;
  }

  public WorkspaceRead updateWorkspace(WorkspaceUpdate workspaceUpdate) {
    final String workspaceId = workspaceUpdate.getWorkspaceId().toString();

    final StandardWorkspaceConfiguration persistedWorkspace =
        configPersistence.getConfig(
            PersistenceConfigType.STANDARD_WORKSPACE_CONFIGURATION,
            workspaceId,
            StandardWorkspaceConfiguration.class);

    if (workspaceUpdate.getEmail() != null && !workspaceUpdate.getEmail().equals("")) {
      persistedWorkspace.setEmail(workspaceUpdate.getEmail());
    }
    persistedWorkspace.setInitialSetupComplete(workspaceUpdate.getInitialSetupComplete());
    persistedWorkspace.setAnonymousDataCollection(workspaceUpdate.getNews());
    persistedWorkspace.setNews(workspaceUpdate.getNews());
    persistedWorkspace.setSecurityUpdates(workspaceUpdate.getSecurityUpdates());

    return getWorkspaceFromId(workspaceUpdate.getWorkspaceId());
  }
}
