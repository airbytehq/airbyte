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

import static io.airbyte.api.model.CheckConnectionRead.StatusEnum.SUCCEEDED;

import com.google.api.client.util.Preconditions;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceRecreate;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.ConnectFailureKnownException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WebBackendSourceHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebBackendSourceHandler.class);

  private final SourceHandler sourceHandler;

  private final SchedulerHandler schedulerHandler;
  private final WorkspaceHelper workspaceHelper;

  public WebBackendSourceHandler(final SourceHandler sourceHandler, final SchedulerHandler schedulerHandler, final WorkspaceHelper workspaceHelper) {
    this.sourceHandler = sourceHandler;
    this.schedulerHandler = schedulerHandler;
    this.workspaceHelper = workspaceHelper;
  }

  public SourceRead webBackendRecreateSourceAndCheck(SourceRecreate sourceRecreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    Preconditions
        .checkArgument(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceRecreate.getSourceId()).equals(sourceRecreate.getWorkspaceId()));

    final SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setConnectionConfiguration(sourceRecreate.getConnectionConfiguration());
    sourceCreate.setName(sourceRecreate.getName());
    sourceCreate.setWorkspaceId(sourceRecreate.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRecreate.getSourceDefinitionId());

    final SourceRead source = sourceHandler.createSource(sourceCreate);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(source.getSourceId());

    try {
      final CheckConnectionRead checkConnectionRead = schedulerHandler
          .checkSourceConnectionFromSourceId(sourceIdRequestBody);
      if (checkConnectionRead.getStatus() == SUCCEEDED) {
        final SourceIdRequestBody sourceIdRequestBody1 = new SourceIdRequestBody().sourceId(sourceRecreate.getSourceId());
        sourceHandler.deleteSource(sourceIdRequestBody1);
        return source;
      }
    } catch (Exception e) {
      LOGGER.error("Error while checking connection", e);
    }

    sourceHandler.deleteSource(sourceIdRequestBody);
    throw new ConnectFailureKnownException("Unable to connect to source");
  }

}
