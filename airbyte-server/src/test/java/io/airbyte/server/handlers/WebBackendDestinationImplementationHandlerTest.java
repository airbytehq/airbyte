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
import io.airbyte.api.model.DestinationImplementationCreate;
import io.airbyte.api.model.DestinationImplementationIdRequestBody;
import io.airbyte.api.model.DestinationImplementationRead;
import io.airbyte.api.model.DestinationImplementationRecreate;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.DestinationImplementationHelpers;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class WebBackendDestinationImplementationHandlerTest {

  private WebBackendDestinationImplementationHandler wbDestinationImplementationHandler;

  private DestinationImplementationsHandler destinationImplementationsHandler;
  private SchedulerHandler schedulerHandler;

  private DestinationImplementationRead destinationImplementationRead;

  @BeforeEach
  public void setup() throws IOException {
    destinationImplementationsHandler = mock(DestinationImplementationsHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    wbDestinationImplementationHandler = new WebBackendDestinationImplementationHandler(destinationImplementationsHandler, schedulerHandler);

    final StandardDestination standardDestination = DestinationHelpers.generateDestination();
    DestinationConnectionImplementation destinationImplementation =
        DestinationImplementationHelpers.generateDestinationImplementation(UUID.randomUUID());
    destinationImplementationRead = DestinationImplementationHelpers.getDestinationImplementationRead(destinationImplementation, standardDestination);
  }

  @Test
  public void testCreatesDestinationWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate();
    destinationImplementationCreate.setName(destinationImplementationRead.getName());
    destinationImplementationCreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationCreate.setDestinationId(destinationImplementationRead.getDestinationId());
    destinationImplementationCreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());

    when(destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate))
        .thenReturn(destinationImplementationRead);

    DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(destinationImplementationRead.getDestinationImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCESS);

    when(schedulerHandler.checkDestinationImplementationConnection(destinationImplementationIdRequestBody)).thenReturn(checkConnectionRead);

    DestinationImplementationRead returnedDestination =
        wbDestinationImplementationHandler.webBackendCreateDestinationImplementationAndCheck(destinationImplementationCreate);

    verify(destinationImplementationsHandler, times(0)).deleteDestinationImplementation(Mockito.any());
    assertEquals(destinationImplementationRead, returnedDestination);
  }

  @Test
  public void testDeletesDestinationWhenCheckConnectionFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate();
    destinationImplementationCreate.setName(destinationImplementationRead.getName());
    destinationImplementationCreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationCreate.setDestinationId(destinationImplementationRead.getDestinationId());
    destinationImplementationCreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());

    when(destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate))
        .thenReturn(destinationImplementationRead);

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILURE);

    DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody();
    destinationImplementationIdRequestBody.setDestinationImplementationId(destinationImplementationRead.getDestinationImplementationId());
    when(schedulerHandler.checkDestinationImplementationConnection(destinationImplementationIdRequestBody)).thenReturn(checkConnectionRead);

    Assertions.assertThrows(KnownException.class,
        () -> wbDestinationImplementationHandler.webBackendCreateDestinationImplementationAndCheck(destinationImplementationCreate));

    verify(destinationImplementationsHandler).deleteDestinationImplementation(destinationImplementationIdRequestBody);
  }

  @Test
  public void testReCreatesDestinationWhenCheckConnectionSucceeds() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate();
    destinationImplementationCreate.setName(destinationImplementationRead.getName());
    destinationImplementationCreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationCreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());

    DestinationImplementationRead newDestinationImplementation = DestinationImplementationHelpers
        .getDestinationImplementationRead(DestinationImplementationHelpers.generateDestinationImplementation(UUID.randomUUID()), DestinationHelpers
            .generateDestination());

    when(destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate)).thenReturn(newDestinationImplementation);

    DestinationImplementationIdRequestBody newDestinationId = new DestinationImplementationIdRequestBody();
    newDestinationId.setDestinationImplementationId(newDestinationImplementation.getDestinationImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.SUCCESS);

    when(schedulerHandler.checkDestinationImplementationConnection(newDestinationId)).thenReturn(checkConnectionRead);

    DestinationImplementationRecreate destinationImplementationRecreate = new DestinationImplementationRecreate();
    destinationImplementationRecreate.setName(destinationImplementationRead.getName());
    destinationImplementationRecreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationRecreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());
    destinationImplementationRecreate.setDestinationImplementationId(destinationImplementationRead.getDestinationImplementationId());

    DestinationImplementationIdRequestBody oldDestinationIdBody = new DestinationImplementationIdRequestBody();
    oldDestinationIdBody.setDestinationImplementationId(destinationImplementationRead.getDestinationImplementationId());

    DestinationImplementationRead returnedDestination =
        wbDestinationImplementationHandler.webBackendRecreateDestinationImplementationAndCheck(destinationImplementationRecreate);

    verify(destinationImplementationsHandler, times(1)).deleteDestinationImplementation(Mockito.eq(oldDestinationIdBody));
    assertEquals(newDestinationImplementation, returnedDestination);
  }

  @Test
  public void testRecreateDeletesNewCreatedDestinationWhenFails() throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate();
    destinationImplementationCreate.setName(destinationImplementationRead.getName());
    destinationImplementationCreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationCreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());

    DestinationImplementationRead newDestinationImplementation = DestinationImplementationHelpers.getDestinationImplementationRead(
        DestinationImplementationHelpers.generateDestinationImplementation(UUID.randomUUID()), DestinationHelpers.generateDestination());

    when(destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate)).thenReturn(newDestinationImplementation);

    DestinationImplementationIdRequestBody newDestinationId = new DestinationImplementationIdRequestBody();
    newDestinationId.setDestinationImplementationId(newDestinationImplementation.getDestinationImplementationId());

    CheckConnectionRead checkConnectionRead = new CheckConnectionRead();
    checkConnectionRead.setStatus(StatusEnum.FAILURE);

    when(schedulerHandler.checkDestinationImplementationConnection(newDestinationId)).thenReturn(checkConnectionRead);

    DestinationImplementationRecreate destinationImplementationRecreate = new DestinationImplementationRecreate();
    destinationImplementationRecreate.setName(destinationImplementationRead.getName());
    destinationImplementationRecreate.setConnectionConfiguration(destinationImplementationRead.getConnectionConfiguration());
    destinationImplementationRecreate.setWorkspaceId(destinationImplementationRead.getWorkspaceId());
    destinationImplementationRecreate.setDestinationImplementationId(destinationImplementationRead.getDestinationImplementationId());

    Assertions.assertThrows(KnownException.class,
        () -> wbDestinationImplementationHandler.webBackendRecreateDestinationImplementationAndCheck(destinationImplementationRecreate));
    verify(destinationImplementationsHandler, times(1)).deleteDestinationImplementation(Mockito.eq(newDestinationId));
  }

}
