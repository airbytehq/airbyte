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

import com.google.common.base.Strings;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.SlugRequestBody;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.api.model.WorkspaceRead;
import io.airbyte.api.model.WorkspaceUpdate;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.validation.json.JsonValidationException;
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
  public WorkspaceRead getWorkspaceBySlug(SlugRequestBody slugRequestBody) throws JsonValidationException, IOException, ConfigNotFoundException {
    // for now we assume there is one workspace and it has a default uuid.
    return buildWorkspaceReadFromId(PersistenceConstants.DEFAULT_WORKSPACE_ID);
  }

  public WorkspaceRead updateWorkspace(WorkspaceUpdate workspaceUpdate) throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID workspaceId = workspaceUpdate.getWorkspaceId();

    final StandardWorkspace persistedWorkspace = configRepository.getStandardWorkspace(workspaceId);

    if (!Strings.isNullOrEmpty(workspaceUpdate.getEmail())) {
      persistedWorkspace.withEmail(workspaceUpdate.getEmail());
    }
    persistedWorkspace
        .withOnboardingComplete(workspaceUpdate.getOnboardingComplete())
        .withInitialSetupComplete(workspaceUpdate.getInitialSetupComplete())
        .withAnonymousDataCollection(workspaceUpdate.getAnonymousDataCollection())
        .withNews(workspaceUpdate.getNews())
        .withSecurityUpdates(workspaceUpdate.getSecurityUpdates())
        .withDisplaySetupWizard(workspaceUpdate.getDisplaySetupWizard());

    configRepository.writeStandardWorkspace(persistedWorkspace);

    // after updating email or tracking info, we need to re-identify the instance.
    TrackingClientSingleton.get().identify();

    return buildWorkspaceReadFromId(workspaceUpdate.getWorkspaceId());
  }

  private WorkspaceRead buildWorkspaceReadFromId(UUID workspaceId) throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId);

    return new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(workspace.getInitialSetupComplete())
        .onboardingComplete(workspace.getOnboardingComplete())
        .displaySetupWizard(workspace.getDisplaySetupWizard());
  }

}
