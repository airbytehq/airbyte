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
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConstants;
import java.io.IOException;
import java.util.UUID;

public class WorkspacesHandler {

  private final ConfigRepository configRepository;

  public WorkspacesHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public WorkspaceRead getWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildWorkspaceReadFromId(workspaceIdRequestBody.getWorkspaceId());
  }

  @SuppressWarnings("unused")
  public WorkspaceRead getWorkspaceBySlug(SlugRequestBody slugRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // for now we assume there is one workspace and it has a default uuid.
    return buildWorkspaceReadFromId(PersistenceConstants.DEFAULT_WORKSPACE_ID);
  }

  public WorkspaceRead updateWorkspace(WorkspaceUpdate workspaceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID workspaceId = workspaceUpdate.getWorkspaceId();

    final StandardWorkspace persistedWorkspace = configRepository.getStandardWorkspace(workspaceId);

    if (workspaceUpdate.getEmail() != null && !workspaceUpdate.getEmail().equals("")) {
      persistedWorkspace.withEmail(workspaceUpdate.getEmail());
    }
    persistedWorkspace.withInitialSetupComplete(workspaceUpdate.getInitialSetupComplete())
        .withAnonymousDataCollection(workspaceUpdate.getAnonymousDataCollection())
        .withNews(workspaceUpdate.getNews())
        .withSecurityUpdates(workspaceUpdate.getSecurityUpdates());

    configRepository.writeStandardWorkspace(persistedWorkspace);

    return buildWorkspaceReadFromId(workspaceUpdate.getWorkspaceId());
  }

  private WorkspaceRead buildWorkspaceReadFromId(UUID workspaceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId);

    return new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(workspace.getInitialSetupComplete());
  }

}
