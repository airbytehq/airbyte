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

import io.airbyte.api.model.*;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.errors.KnownException;

import java.io.IOException;

public class WebBackendDestinationImplementationHandler {

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

        CheckConnectionRead checkConnectionRead = null;

        boolean syncFailed;
        try {
            checkConnectionRead = schedulerHandler
                    .checkDestinationImplementationConnection(destinationImplementationIdRequestBody);
        } finally {
            syncFailed = checkConnectionRead == null
                    || CheckConnectionRead.StatusEnum.FAILURE == checkConnectionRead.getStatus();
            if (syncFailed) {
                destinationImplementationsHandler
                        .deleteDestinationImplementation(destinationImplementationIdRequestBody);
            }
        }

        if (syncFailed) {
            throw new KnownException(400, "Unable to connect to destination");
        }

        return destinationImplementation;
    }

}
