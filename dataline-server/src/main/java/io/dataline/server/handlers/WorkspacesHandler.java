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
    return getWorkspaceFromId(PersistenceConstants.DEFAULT_WORKSPACE_ID);
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
