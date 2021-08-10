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
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationRecreate;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class WebBackendDestinationHandlerTest {

  private WebBackendDestinationHandler wbDestinationHandler;

  private DestinationHandler destinationHandler;
  private SchedulerHandler schedulerHandler;
  private WorkspaceHelper workspaceHelper;

  private DestinationRead destinationRead;

  @BeforeEach
  public void setup() throws IOException {
    destinationHandler = mock(DestinationHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    wbDestinationHandler = new WebBackendDestinationHandler(destinationHandler, schedulerHandler, workspaceHelper);

    final StandardDestinationDefinition standardDestinationDefinition = DestinationDefinitionHelpers.generateDestination();
    DestinationConnection destination =
        DestinationHelpers.generateDestination(UUID.randomUUID());
    destinationRead = DestinationHelpers.getDestinationRead(destination, standardDestinationDefinition);

    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationRead.getDestinationId()))
        .thenReturn(destinationRead.getWorkspaceId());
  }

  @Test
  public void testReCreatesDestinationWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationCreate destinationCreate = new DestinationCreate();
    destinationCreate.setName(destinationRead.getName());
    destinationCreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationCreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationCreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    DestinationRead newDestination = DestinationHelpers
        .getDestinationRead(DestinationHelpers.generateDestination(UUID.randomUUID()), DestinationDefinitionHelpers
            .generateDestination());

    when(destinationHandler.createDestination(destinationCreate)).thenReturn(newDestination);

    DestinationIdRequestBody newDestinationId = new DestinationIdRequestBody();
    newDestinationId.setDestinationId(newDestination.getDestinationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCEEDED);

    when(schedulerHandler.checkDestinationConnectionFromDestinationId(newDestinationId)).thenReturn(checkConnectionRead);

    DestinationRecreate destinationRecreate = new DestinationRecreate();
    destinationRecreate.setName(destinationRead.getName());
    destinationRecreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationRecreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationRecreate.setDestinationId(destinationRead.getDestinationId());
    destinationRecreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    DestinationIdRequestBody oldDestinationIdBody = new DestinationIdRequestBody();
    oldDestinationIdBody.setDestinationId(destinationRead.getDestinationId());

    DestinationRead returnedDestination =
        wbDestinationHandler.webBackendRecreateDestinationAndCheck(destinationRecreate);

    verify(destinationHandler, times(1)).deleteDestination(Mockito.eq(oldDestinationIdBody));
    assertEquals(newDestination, returnedDestination);
  }

  @Test
  public void testRecreateDeletesNewCreatedDestinationWhenFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationCreate destinationCreate = new DestinationCreate();
    destinationCreate.setName(destinationRead.getName());
    destinationCreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationCreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationCreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    DestinationRead newDestination = DestinationHelpers.getDestinationRead(
        DestinationHelpers.generateDestination(UUID.randomUUID()), DestinationDefinitionHelpers.generateDestination());

    when(destinationHandler.createDestination(destinationCreate)).thenReturn(newDestination);

    DestinationIdRequestBody newDestinationId = new DestinationIdRequestBody();
    newDestinationId.setDestinationId(newDestination.getDestinationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILED);

    when(schedulerHandler.checkDestinationConnectionFromDestinationId(newDestinationId)).thenReturn(checkConnectionRead);

    DestinationRecreate destinationRecreate = new DestinationRecreate();
    destinationRecreate.setName(destinationRead.getName());
    destinationRecreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationRecreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationRecreate.setDestinationId(destinationRead.getDestinationId());
    destinationRecreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    Assertions.assertThrows(KnownException.class,
        () -> wbDestinationHandler.webBackendRecreateDestinationAndCheck(destinationRecreate));
    verify(destinationHandler, times(1)).deleteDestination(Mockito.eq(newDestinationId));
  }

  @Test
  public void testUnmatchedWorkspaces() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationRead.getDestinationId())).thenReturn(UUID.randomUUID());

    DestinationCreate destinationCreate = new DestinationCreate();
    destinationCreate.setName(destinationRead.getName());
    destinationCreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationCreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationCreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    DestinationRead newDestination = DestinationHelpers
        .getDestinationRead(DestinationHelpers.generateDestination(UUID.randomUUID()), DestinationDefinitionHelpers
            .generateDestination());

    when(destinationHandler.createDestination(destinationCreate)).thenReturn(newDestination);

    DestinationIdRequestBody newDestinationId = new DestinationIdRequestBody();
    newDestinationId.setDestinationId(newDestination.getDestinationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCEEDED);

    when(schedulerHandler.checkDestinationConnectionFromDestinationId(newDestinationId)).thenReturn(checkConnectionRead);

    DestinationRecreate destinationRecreate = new DestinationRecreate();
    destinationRecreate.setName(destinationRead.getName());
    destinationRecreate.setConnectionConfiguration(destinationRead.getConnectionConfiguration());
    destinationRecreate.setWorkspaceId(destinationRead.getWorkspaceId());
    destinationRecreate.setDestinationId(destinationRead.getDestinationId());
    destinationRecreate.setDestinationDefinitionId(destinationRead.getDestinationDefinitionId());

    DestinationIdRequestBody oldDestinationIdBody = new DestinationIdRequestBody();
    oldDestinationIdBody.setDestinationId(destinationRead.getDestinationId());

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      wbDestinationHandler.webBackendRecreateDestinationAndCheck(destinationRecreate);
    });
  }

}
