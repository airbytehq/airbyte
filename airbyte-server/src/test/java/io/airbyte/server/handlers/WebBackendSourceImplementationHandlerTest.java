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
import io.airbyte.api.model.SourceImplementationCreate;
import io.airbyte.api.model.SourceImplementationIdRequestBody;
import io.airbyte.api.model.SourceImplementationRead;
import io.airbyte.api.model.SourceImplementationRecreate;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.server.helpers.SourceImplementationHelpers;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class WebBackendSourceImplementationHandlerTest {

  private WebBackendSourceImplementationHandler wbSourceImplementationHandler;

  private SourceImplementationsHandler sourceImplementationsHandler;
  private SchedulerHandler schedulerHandler;

  private SourceImplementationRead sourceImplementationRead;

  @BeforeEach
  public void setup() throws IOException {
    sourceImplementationsHandler = mock(SourceImplementationsHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    wbSourceImplementationHandler = new WebBackendSourceImplementationHandler(sourceImplementationsHandler, schedulerHandler);

    final StandardSource standardSource = SourceHelpers.generateSource();
    SourceConnectionImplementation sourceImplementation = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID());
    sourceImplementationRead = SourceImplementationHelpers.getSourceImplementationRead(sourceImplementation, standardSource);
  }

  @Test
  public void testCreatesSourceWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setName(sourceImplementationRead.getName());
    sourceImplementationCreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationCreate.setSourceId(sourceImplementationRead.getSourceId());
    sourceImplementationCreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());

    when(sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate)).thenReturn(sourceImplementationRead);

    SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(sourceImplementationRead.getSourceImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCESS);

    when(schedulerHandler.checkSourceImplementationConnection(sourceImplementationIdRequestBody)).thenReturn(checkConnectionRead);

    SourceImplementationRead returnedSource = wbSourceImplementationHandler.webBackendCreateSourceImplementationAndCheck(sourceImplementationCreate);

    verify(sourceImplementationsHandler, times(0)).deleteSourceImplementation(Mockito.any());
    assertEquals(sourceImplementationRead, returnedSource);
  }

  @Test
  public void testDeletesSourceWhenCheckConnectionFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setName(sourceImplementationRead.getName());
    sourceImplementationCreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationCreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());
    when(sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate)).thenReturn(sourceImplementationRead);

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILURE);

    SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(sourceImplementationRead.getSourceImplementationId());
    when(schedulerHandler.checkSourceImplementationConnection(sourceImplementationIdRequestBody)).thenReturn(checkConnectionRead);

    Assertions.assertThrows(KnownException.class,
        () -> wbSourceImplementationHandler.webBackendCreateSourceImplementationAndCheck(sourceImplementationCreate));

    verify(sourceImplementationsHandler).deleteSourceImplementation(sourceImplementationIdRequestBody);
  }

  @Test
  public void testReCreatesSourceWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setName(sourceImplementationRead.getName());
    sourceImplementationCreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationCreate.setSourceSpecificationId(sourceImplementationRead.getSourceSpecificationId());
    sourceImplementationCreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());

    SourceImplementationRead newSourceImplementation = SourceImplementationHelpers
        .getSourceImplementationRead(SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID()), SourceHelpers.generateSource());

    when(sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate)).thenReturn(newSourceImplementation);

    SourceImplementationIdRequestBody newSourceId = new SourceImplementationIdRequestBody();
    newSourceId.setSourceImplementationId(newSourceImplementation.getSourceImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCESS);

    when(schedulerHandler.checkSourceImplementationConnection(newSourceId)).thenReturn(checkConnectionRead);

    SourceImplementationRecreate sourceImplementationRecreate = new SourceImplementationRecreate();
    sourceImplementationRecreate.setName(sourceImplementationRead.getName());
    sourceImplementationRecreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationRecreate.setSourceSpecificationId(sourceImplementationRead.getSourceSpecificationId());
    sourceImplementationRecreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());
    sourceImplementationRecreate.setSourceImplementationId(sourceImplementationRead.getSourceImplementationId());

    SourceImplementationIdRequestBody oldSourceIdBody = new SourceImplementationIdRequestBody();
    oldSourceIdBody.setSourceImplementationId(sourceImplementationRead.getSourceImplementationId());

    SourceImplementationRead returnedSource =
        wbSourceImplementationHandler.webBackendRecreateSourceImplementationAndCheck(sourceImplementationRecreate);

    verify(sourceImplementationsHandler, times(1)).deleteSourceImplementation(Mockito.eq(oldSourceIdBody));
    assertEquals(newSourceImplementation, returnedSource);
  }

  @Test
  public void testRecreateDeletesNewCreatedSourceWhenFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate();
    sourceImplementationCreate.setName(sourceImplementationRead.getName());
    sourceImplementationCreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationCreate.setSourceSpecificationId(sourceImplementationRead.getSourceSpecificationId());
    sourceImplementationCreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());

    SourceImplementationRead newSourceImplementation = SourceImplementationHelpers
        .getSourceImplementationRead(SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID()), SourceHelpers.generateSource());

    when(sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate)).thenReturn(newSourceImplementation);

    SourceImplementationIdRequestBody newSourceId = new SourceImplementationIdRequestBody();
    newSourceId.setSourceImplementationId(newSourceImplementation.getSourceImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILURE);

    when(schedulerHandler.checkSourceImplementationConnection(newSourceId)).thenReturn(checkConnectionRead);

    SourceImplementationRecreate sourceImplementationRecreate = new SourceImplementationRecreate();
    sourceImplementationRecreate.setName(sourceImplementationRead.getName());
    sourceImplementationRecreate.setConnectionConfiguration(sourceImplementationRead.getConnectionConfiguration());
    sourceImplementationRecreate.setSourceSpecificationId(sourceImplementationRead.getSourceSpecificationId());
    sourceImplementationRecreate.setWorkspaceId(sourceImplementationRead.getWorkspaceId());
    sourceImplementationRecreate.setSourceImplementationId(sourceImplementationRead.getSourceImplementationId());

    Assertions.assertThrows(KnownException.class,
        () -> wbSourceImplementationHandler.webBackendRecreateSourceImplementationAndCheck(sourceImplementationRecreate));
    verify(sourceImplementationsHandler, times(1)).deleteSourceImplementation(Mockito.eq(newSourceId));
  }

}
