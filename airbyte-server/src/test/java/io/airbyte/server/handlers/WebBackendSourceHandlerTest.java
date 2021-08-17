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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.CheckConnectionRead.StatusEnum;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceRecreate;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class WebBackendSourceHandlerTest {

  private WebBackendSourceHandler wbSourceHandler;

  private SourceHandler sourceHandler;
  private SchedulerHandler schedulerHandler;
  private WorkspaceHelper workspaceHelper;

  private SourceRead sourceRead;

  @BeforeEach
  public void setup() throws IOException {
    sourceHandler = mock(SourceHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    wbSourceHandler = new WebBackendSourceHandler(sourceHandler, schedulerHandler, workspaceHelper);

    final StandardSourceDefinition standardSourceDefinition = SourceDefinitionHelpers.generateSource();
    SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceRead.getSourceId())).thenReturn(sourceRead.getWorkspaceId());
  }

  @Test
  public void testReCreatesSourceWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setName(sourceRead.getName());
    sourceCreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceCreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    SourceRead newSource = SourceHelpers
        .getSourceRead(SourceHelpers.generateSource(UUID.randomUUID()), SourceDefinitionHelpers.generateSource());

    when(sourceHandler.createSource(sourceCreate)).thenReturn(newSource);

    SourceIdRequestBody newSourceId = new SourceIdRequestBody();
    newSourceId.setSourceId(newSource.getSourceId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCEEDED);

    when(schedulerHandler.checkSourceConnectionFromSourceId(newSourceId)).thenReturn(checkConnectionRead);

    SourceRecreate sourceRecreate = new SourceRecreate();
    sourceRecreate.setName(sourceRead.getName());
    sourceRecreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceRecreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceRecreate.setSourceId(sourceRead.getSourceId());
    sourceRecreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    SourceIdRequestBody oldSourceIdBody = new SourceIdRequestBody();
    oldSourceIdBody.setSourceId(sourceRead.getSourceId());

    SourceRead returnedSource =
        wbSourceHandler.webBackendRecreateSourceAndCheck(sourceRecreate);

    verify(sourceHandler, times(1)).deleteSource(Mockito.eq(oldSourceIdBody));
    assertEquals(newSource, returnedSource);
  }

  @Test
  public void testRecreateDeletesNewCreatedSourceWhenFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setName(sourceRead.getName());
    sourceCreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceCreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    SourceRead newSource = SourceHelpers
        .getSourceRead(SourceHelpers.generateSource(sourceRead.getSourceDefinitionId()), SourceDefinitionHelpers.generateSource());

    when(sourceHandler.createSource(sourceCreate)).thenReturn(newSource);

    SourceIdRequestBody newSourceId = new SourceIdRequestBody();
    newSourceId.setSourceId(newSource.getSourceId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILED);

    when(schedulerHandler.checkSourceConnectionFromSourceId(newSourceId)).thenReturn(checkConnectionRead);

    SourceRecreate sourceRecreate = new SourceRecreate();
    sourceRecreate.setName(sourceRead.getName());
    sourceRecreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceRecreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceRecreate.setSourceId(sourceRead.getSourceId());
    sourceRecreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    Assertions.assertThrows(KnownException.class,
        () -> wbSourceHandler.webBackendRecreateSourceAndCheck(sourceRecreate));
    verify(sourceHandler, times(1)).deleteSource(Mockito.eq(newSourceId));
  }

  @Test
  public void testUnmatchedWorkspaces() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceRead.getSourceId())).thenReturn(UUID.randomUUID());

    SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setName(sourceRead.getName());
    sourceCreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceCreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    SourceRead newSource = SourceHelpers
        .getSourceRead(SourceHelpers.generateSource(UUID.randomUUID()), SourceDefinitionHelpers.generateSource());

    when(sourceHandler.createSource(sourceCreate)).thenReturn(newSource);

    SourceIdRequestBody newSourceId = new SourceIdRequestBody();
    newSourceId.setSourceId(newSource.getSourceId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCEEDED);

    when(schedulerHandler.checkSourceConnectionFromSourceId(newSourceId)).thenReturn(checkConnectionRead);

    SourceRecreate sourceRecreate = new SourceRecreate();
    sourceRecreate.setName(sourceRead.getName());
    sourceRecreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceRecreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceRecreate.setSourceId(sourceRead.getSourceId());
    sourceRecreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    SourceIdRequestBody oldSourceIdBody = new SourceIdRequestBody();
    oldSourceIdBody.setSourceId(sourceRead.getSourceId());

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      wbSourceHandler.webBackendRecreateSourceAndCheck(sourceRecreate);
    });
  }

}
