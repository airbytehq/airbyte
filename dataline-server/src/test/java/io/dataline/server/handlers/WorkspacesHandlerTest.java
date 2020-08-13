package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.*;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkspacesHandlerTest {
  private ConfigPersistenceImpl configPersistence;
  private StandardWorkspace workspace;
  private WorkspacesHandler workspacesHandler;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();
    workspace = creatWorkspace();
    workspacesHandler = new WorkspacesHandler(configPersistence);
  }

  private StandardWorkspace creatWorkspace() {
    final UUID workspaceId = WorkspaceConstants.DEFAULT_WORKSPACE_ID;

    final StandardWorkspace standardWorkspace = new StandardWorkspace();
    standardWorkspace.setWorkspaceId(workspaceId);
    standardWorkspace.setEmail("test@dataline.io");
    standardWorkspace.setName("test workspace");
    standardWorkspace.setSlug("default");
    standardWorkspace.setInitialSetupComplete(false);

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_WORKSPACE, workspaceId.toString(), standardWorkspace);

    return standardWorkspace;
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  @Test
  void getWorkspace() {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(workspace.getWorkspaceId());

    final WorkspaceRead workspaceRead = new WorkspaceRead();
    workspaceRead.setWorkspaceId(workspace.getWorkspaceId());
    workspaceRead.setName("test workspace");
    workspaceRead.setSlug("default");
    workspaceRead.setInitialSetupComplete(false);

    assertEquals(workspaceRead, workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Test
  void getWorkspaceBySlug() {
    final SlugRequestBody slugRequestBody = new SlugRequestBody();
    slugRequestBody.setSlug("default");

    final WorkspaceRead workspaceRead = new WorkspaceRead();
    workspaceRead.setWorkspaceId(workspace.getWorkspaceId());
    workspaceRead.setName("test workspace");
    workspaceRead.setSlug("default");
    workspaceRead.setInitialSetupComplete(false);

    assertEquals(workspaceRead, workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Test
  void updateWorkspace() {
    final WorkspaceUpdate workspaceUpdate = new WorkspaceUpdate();
    workspaceUpdate.setWorkspaceId(workspace.getWorkspaceId());
    workspaceUpdate.setAnonymousDataCollection(true);
    workspaceUpdate.setSecurityUpdates(false);
    workspaceUpdate.setNews(false);
    workspaceUpdate.setInitialSetupComplete(true);
    workspacesHandler.updateWorkspace(workspaceUpdate);

    final StandardWorkspace persistedWorkspace;
    try {
      persistedWorkspace =
          configPersistence.getConfig(
              PersistenceConfigType.STANDARD_WORKSPACE,
              workspace.getWorkspaceId().toString(),
              StandardWorkspace.class);
    } catch (ConfigNotFoundException | JsonValidationException e) {
      fail();
      return;
    }

    final StandardWorkspace expectedWorkspace = new StandardWorkspace();
    expectedWorkspace.setWorkspaceId(workspace.getWorkspaceId());
    expectedWorkspace.setEmail("test@dataline.io");
    expectedWorkspace.setName("test workspace");
    expectedWorkspace.setSlug("default");
    expectedWorkspace.setAnonymousDataCollection(true);
    expectedWorkspace.setSecurityUpdates(false);
    expectedWorkspace.setNews(false);
    expectedWorkspace.setInitialSetupComplete(true);

    assertEquals(expectedWorkspace, persistedWorkspace);
  }
}
