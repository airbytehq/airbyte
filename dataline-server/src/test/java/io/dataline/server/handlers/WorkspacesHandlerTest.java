/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.config.persistence.PersistenceConstants;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkspacesHandlerTest {
  private ConfigPersistence configPersistence;
  private StandardWorkspace workspace;
  private WorkspacesHandler workspacesHandler;

  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    workspace = generateWorkspace();
    workspacesHandler = new WorkspacesHandler(configPersistence);
  }

  private StandardWorkspace generateWorkspace() {
    final UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;

    final StandardWorkspace standardWorkspace = new StandardWorkspace();
    standardWorkspace.setWorkspaceId(workspaceId);
    standardWorkspace.setEmail("test@dataline.io");
    standardWorkspace.setName("test workspace");
    standardWorkspace.setSlug("default");
    standardWorkspace.setInitialSetupComplete(false);

    return standardWorkspace;
  }

  @Test
  void testGetWorkspace() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_WORKSPACE,
            workspace.getWorkspaceId().toString(),
            StandardWorkspace.class))
        .thenReturn(workspace);

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
  void testGetWorkspaceBySlug() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_WORKSPACE,
            workspace.getWorkspaceId().toString(),
            StandardWorkspace.class))
        .thenReturn(workspace);

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
  void testUpdateWorkspace() throws JsonValidationException, ConfigNotFoundException {

    final WorkspaceUpdate workspaceUpdate = new WorkspaceUpdate();
    workspaceUpdate.setWorkspaceId(workspace.getWorkspaceId());
    workspaceUpdate.setAnonymousDataCollection(true);
    workspaceUpdate.setSecurityUpdates(false);
    workspaceUpdate.setNews(false);
    workspaceUpdate.setInitialSetupComplete(true);

    final StandardWorkspace expectedWorkspace = new StandardWorkspace();
    expectedWorkspace.setWorkspaceId(workspace.getWorkspaceId());
    expectedWorkspace.setEmail("test@dataline.io");
    expectedWorkspace.setName("test workspace");
    expectedWorkspace.setSlug("default");
    expectedWorkspace.setAnonymousDataCollection(true);
    expectedWorkspace.setSecurityUpdates(false);
    expectedWorkspace.setNews(false);
    expectedWorkspace.setInitialSetupComplete(true);

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_WORKSPACE,
            workspace.getWorkspaceId().toString(),
            StandardWorkspace.class))
        .thenReturn(workspace)
        .thenReturn(expectedWorkspace);

    final WorkspaceRead actualWorkspaceRead = workspacesHandler.updateWorkspace(workspaceUpdate);

    final WorkspaceRead expectedWorkspaceRead = new WorkspaceRead();
    expectedWorkspaceRead.setWorkspaceId(workspace.getWorkspaceId());
    expectedWorkspaceRead.setName("test workspace");
    expectedWorkspaceRead.setSlug("default");
    expectedWorkspaceRead.setInitialSetupComplete(true);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.STANDARD_WORKSPACE,
            expectedWorkspace.getWorkspaceId().toString(),
            expectedWorkspace);

    assertEquals(expectedWorkspaceRead, actualWorkspaceRead);
  }
}
