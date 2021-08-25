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
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationRecreate;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.ConnectFailureKnownException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WebBackendDestinationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebBackendDestinationHandler.class);

  private final DestinationHandler destinationHandler;

  private final SchedulerHandler schedulerHandler;
  private final WorkspaceHelper workspaceHelper;

  public WebBackendDestinationHandler(final DestinationHandler destinationHandler,
                                      final SchedulerHandler schedulerHandler,
                                      final WorkspaceHelper workspaceHelper) {
    this.destinationHandler = destinationHandler;
    this.schedulerHandler = schedulerHandler;
    this.workspaceHelper = workspaceHelper;
  }

  public DestinationRead webBackendRecreateDestinationAndCheck(DestinationRecreate destinationRecreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    Preconditions.checkArgument(
        workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationRecreate.getDestinationId())
            .equals(destinationRecreate.getWorkspaceId()));

    final DestinationCreate destinationCreate = new DestinationCreate();
    destinationCreate.setConnectionConfiguration(destinationRecreate.getConnectionConfiguration());
    destinationCreate.setName(destinationRecreate.getName());
    destinationCreate.setWorkspaceId(destinationRecreate.getWorkspaceId());
    destinationCreate.setDestinationDefinitionId(destinationRecreate.getDestinationDefinitionId());

    final DestinationRead destination = destinationHandler.createDestination(destinationCreate);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody()
        .destinationId(destination.getDestinationId());

    try {
      final CheckConnectionRead checkConnectionRead = schedulerHandler
          .checkDestinationConnectionFromDestinationId(destinationIdRequestBody);
      if (checkConnectionRead.getStatus() == SUCCEEDED) {
        final DestinationIdRequestBody destinationIdRequestBody1 = new DestinationIdRequestBody()
            .destinationId(destinationRecreate.getDestinationId());

        destinationHandler.deleteDestination(destinationIdRequestBody1);
        return destination;
      }
    } catch (Exception e) {
      LOGGER.error("Error while checking connection", e);
    }

    destinationHandler.deleteDestination(destinationIdRequestBody);
    throw new ConnectFailureKnownException("Unable to connect to destination");
  }

}
