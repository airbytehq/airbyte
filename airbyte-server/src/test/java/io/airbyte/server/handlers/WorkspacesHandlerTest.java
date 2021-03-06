/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.SlugRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.WorkspaceCreate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.api.model.WorkspaceRead;
import io.airbyte.api.model.WorkspaceUpdate;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import javax.ws.rs.NotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkspacesHandlerTest {

  private ConfigRepository configRepository;
  private ConnectionsHandler connectionsHandler;
  private DestinationHandler destinationHandler;
  private SourceHandler sourceHandler;
  private StandardWorkspace workspace;
  private WorkspacesHandler workspacesHandler;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    destinationHandler = mock(DestinationHandler.class);
    sourceHandler = mock(SourceHandler.class);
    workspace = generateWorkspace();
    workspacesHandler = new WorkspacesHandler(configRepository, connectionsHandler, destinationHandler, sourceHandler);
  }

  private StandardWorkspace generateWorkspace() {
    final UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;

    return new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withCustomerId(UUID.randomUUID())
        .withEmail("test@airbyte.io")
        .withName("test workspace")
        .withSlug("default")
        .withInitialSetupComplete(false)
        .withDisplaySetupWizard(true)
        .withNews(false)
        .withAnonymousDataCollection(false)
        .withSecurityUpdates(false)
        .withTombstone(false);
  }

  @Test
  void testCreateWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardWorkspaces())
        .thenReturn(Collections.singletonList(workspace));

    configRepository.writeStandardWorkspace(workspace);

    final WorkspaceCreate workspaceCreate = new WorkspaceCreate()
        .name("new workspace")
        .initialSetupComplete(false)
        .displaySetupWizard(true)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false);

    final WorkspaceRead created = workspacesHandler.createWorkspace(workspaceCreate);

    assertTrue(created.getWorkspaceId() instanceof UUID);
    assertTrue(created.getCustomerId() instanceof UUID);
    assertEquals("new workspace", created.getName());
    assertEquals("new-workspace", created.getSlug());
    assertFalse(created.getInitialSetupComplete());
    assertTrue(created.getDisplaySetupWizard());
    assertFalse(created.getNews());
    assertFalse(created.getAnonymousDataCollection());
    assertFalse(created.getSecurityUpdates());
  }

  @Test
  void testDeleteWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());

    final ConnectionRead connection = new ConnectionRead();
    final DestinationRead destination = new DestinationRead();
    final SourceRead source = new SourceRead();

    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId()))
        .thenReturn(workspace);

    when(configRepository.listStandardWorkspaces())
        .thenReturn(Collections.singletonList(workspace));

    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody))
        .thenReturn(new ConnectionReadList().connections(Collections.singletonList(connection)));

    when(destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody))
        .thenReturn(new DestinationReadList().destinations(Collections.singletonList(destination)));

    when(sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody))
        .thenReturn(new SourceReadList().sources(Collections.singletonList(source)));

    workspacesHandler.deleteWorkspace(workspaceIdRequestBody);

    verify(connectionsHandler).deleteConnection(connection);
    verify(destinationHandler).deleteDestination(destination);
    verify(sourceHandler).deleteSource(source);
  }

  @Test
  void testGetWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId()))
        .thenReturn(workspace);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());

    final WorkspaceRead workspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .name("test workspace")
        .slug("default")
        .initialSetupComplete(false)
        .displaySetupWizard(true)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false);

    assertEquals(workspaceRead, workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Test
  void testGetDeletedWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace deleted = generateWorkspace().withTombstone(true);
    when(configRepository.getStandardWorkspace(deleted.getWorkspaceId()))
        .thenReturn(deleted);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());

    assertThrows(NotFoundException.class, () -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Test
  void testGetWorkspaceBySlug() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardWorkspaces())
        .thenReturn(Collections.singletonList(workspace));

    final SlugRequestBody slugRequestBody = new SlugRequestBody().slug("default");

    final WorkspaceRead workspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .name("test workspace")
        .slug("default")
        .initialSetupComplete(false)
        .displaySetupWizard(true)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false);

    assertEquals(workspaceRead, workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Test
  void testGetDeletedWorkspaceBySlug() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardWorkspaces())
        .thenReturn(Collections.singletonList(generateWorkspace().withTombstone(true)));

    final SlugRequestBody slugRequestBody = new SlugRequestBody().slug("default");
    assertThrows(NotFoundException.class, () -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Test
  void testUpdateWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {

    final WorkspaceUpdate workspaceUpdate = new WorkspaceUpdate()
        .workspaceId(workspace.getWorkspaceId())
        .anonymousDataCollection(true)
        .securityUpdates(false)
        .news(false)
        .initialSetupComplete(true)
        .displaySetupWizard(false);

    final StandardWorkspace expectedWorkspace = new StandardWorkspace()
        .withWorkspaceId(workspace.getWorkspaceId())
        .withCustomerId(workspace.getCustomerId())
        .withEmail("test@airbyte.io")
        .withName("test workspace")
        .withSlug("default")
        .withAnonymousDataCollection(true)
        .withSecurityUpdates(false)
        .withNews(false)
        .withInitialSetupComplete(true)
        .withDisplaySetupWizard(false)
        .withTombstone(false);

    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId()))
        .thenReturn(workspace)
        .thenReturn(expectedWorkspace);

    final WorkspaceRead actualWorkspaceRead = workspacesHandler.updateWorkspace(workspaceUpdate);

    final WorkspaceRead expectedWorkspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .name("test workspace")
        .slug("default")
        .initialSetupComplete(true)
        .displaySetupWizard(false)
        .news(false)
        .anonymousDataCollection(true)
        .securityUpdates(false);

    verify(configRepository).writeStandardWorkspace(expectedWorkspace);

    assertEquals(expectedWorkspaceRead, actualWorkspaceRead);
  }

}
