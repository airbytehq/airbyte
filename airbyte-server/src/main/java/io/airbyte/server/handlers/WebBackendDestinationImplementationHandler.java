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

import static io.airbyte.api.model.CheckConnectionRead.StatusEnum.SUCCESS;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.DestinationImplementationCreate;
import io.airbyte.api.model.DestinationImplementationIdRequestBody;
import io.airbyte.api.model.DestinationImplementationRead;
import io.airbyte.api.model.DestinationImplementationRecreate;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.errors.KnownException;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WebBackendDestinationImplementationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebBackendDestinationImplementationHandler.class);

  private final DestinationImplementationsHandler destinationImplementationsHandler;

  private final SchedulerHandler schedulerHandler;

  public WebBackendDestinationImplementationHandler(
                                                    final DestinationImplementationsHandler destinationImplementationsHandler,
                                                    final SchedulerHandler schedulerHandler) {
    this.destinationImplementationsHandler = destinationImplementationsHandler;
    this.schedulerHandler = schedulerHandler;
  }

  public DestinationImplementationRead webBackendCreateDestinationImplementationAndCheck(
                                                                                         DestinationImplementationCreate destinationImplementationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    DestinationImplementationRead destinationImplementation =
        destinationImplementationsHandler
            .createDestinationImplementation(destinationImplementationCreate);

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody()
        .destinationImplementationId(destinationImplementation.getDestinationImplementationId());

    try {
      CheckConnectionRead checkConnectionRead = schedulerHandler
          .checkDestinationImplementationConnection(destinationImplementationIdRequestBody);
      if (checkConnectionRead.getStatus() == SUCCESS) {
        return destinationImplementation;
      }
    } catch (Exception e) {
      LOGGER.error("Error while checking connection", e);
    }

    destinationImplementationsHandler.deleteDestinationImplementation(destinationImplementationIdRequestBody);
    throw new KnownException(400, "Unable to connect to destination");
  }

  public DestinationImplementationRead webBackendRecreateDestinationImplementationAndCheck(
                                                                                           DestinationImplementationRecreate destinationImplementationRecreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    DestinationImplementationCreate destinationImplementationCreate = new DestinationImplementationCreate();
    destinationImplementationCreate.setConnectionConfiguration(destinationImplementationRecreate.getConnectionConfiguration());
    destinationImplementationCreate.setName(destinationImplementationRecreate.getName());
    destinationImplementationCreate.setWorkspaceId(destinationImplementationRecreate.getWorkspaceId());

    DestinationImplementationRead destinationImplementation =
        destinationImplementationsHandler
            .createDestinationImplementation(destinationImplementationCreate);

    final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody = new DestinationImplementationIdRequestBody()
        .destinationImplementationId(destinationImplementation.getDestinationImplementationId());

    try {
      CheckConnectionRead checkConnectionRead = schedulerHandler
          .checkDestinationImplementationConnection(destinationImplementationIdRequestBody);
      if (checkConnectionRead.getStatus() == SUCCESS) {
        final DestinationImplementationIdRequestBody destinationImplementationIdRequestBody1 = new DestinationImplementationIdRequestBody()
            .destinationImplementationId(destinationImplementationRecreate.getDestinationImplementationId());

        destinationImplementationsHandler.deleteDestinationImplementation(destinationImplementationIdRequestBody1);
        return destinationImplementation;
      }
    } catch (Exception e) {
      LOGGER.error("Error while checking connection", e);
    }

    destinationImplementationsHandler.deleteDestinationImplementation(destinationImplementationIdRequestBody);
    throw new KnownException(400, "Unable to connect to destination");
  }

}
