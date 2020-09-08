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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.dataline.api.model.DestinationImplementationCreate;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.DestinationImplementationRead;
import io.dataline.api.model.DestinationImplementationReadList;
import io.dataline.api.model.DestinationImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.StandardDestination;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class DestinationImplementationsHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final IntegrationSchemaValidation validator;

  public DestinationImplementationsHandler(final ConfigRepository configRepository,
                                           final IntegrationSchemaValidation integrationSchemaValidation,
                                           final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.validator = integrationSchemaValidation;
    this.uuidGenerator = uuidGenerator;
  }

  public DestinationImplementationsHandler(final ConfigRepository configRepository,
                                           final IntegrationSchemaValidation integrationSchemaValidation) {
    this(configRepository, integrationSchemaValidation, UUID::randomUUID);
  }

  public DestinationImplementationRead createDestinationImplementation(final DestinationImplementationCreate destinationImplementationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    validateDestinationImplementation(
        destinationImplementationCreate.getDestinationSpecificationId(),
        destinationImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID destinationImplementationId = uuidGenerator.get();
    persistDestinationConnectionImplementation(
        destinationImplementationCreate.getName() != null ? destinationImplementationCreate.getName() : "default",
        destinationImplementationCreate.getDestinationSpecificationId(),
        destinationImplementationCreate.getWorkspaceId(),
        destinationImplementationId,
        destinationImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return buildDestinationImplementationRead(destinationImplementationId);
  }

  public DestinationImplementationRead updateDestinationImplementation(final DestinationImplementationUpdate destinationImplementationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing implementation
    final DestinationConnectionImplementation dci =
        configRepository.getDestinationConnectionImplementation(destinationImplementationUpdate.getDestinationImplementationId());

    // validate configuration
    validateDestinationImplementation(
        dci.getDestinationSpecificationId(),
        destinationImplementationUpdate.getConnectionConfiguration());

    // persist
    persistDestinationConnectionImplementation(
        destinationImplementationUpdate.getName(),
        dci.getDestinationSpecificationId(),
        dci.getWorkspaceId(),
        destinationImplementationUpdate.getDestinationImplementationId(),
        destinationImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return buildDestinationImplementationRead(destinationImplementationUpdate.getDestinationImplementationId());
  }

  public DestinationImplementationRead getDestinationImplementation(DestinationImplementationIdRequestBody destinationImplementationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildDestinationImplementationRead(destinationImplementationIdRequestBody.getDestinationImplementationId());
  }

  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationImplementationRead> reads = Lists.newArrayList();

    for (DestinationConnectionImplementation dci : configRepository.listDestinationConnectionImplementations()) {
      if (!dci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }

      reads.add(buildDestinationImplementationRead(dci.getDestinationImplementationId()));
    }

    return new DestinationImplementationReadList().destinations(reads);
  }

  private void validateDestinationImplementation(final UUID destinationConnectionSpecificationId,
                                                 final JsonNode implementationJson)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationConnectionSpecification dcs = configRepository.getDestinationConnectionSpecification(destinationConnectionSpecificationId);
    validator.validateConfig(dcs, implementationJson);
  }

  private void persistDestinationConnectionImplementation(final String name,
                                                          final UUID destinationSpecificationId,
                                                          final UUID workspaceId,
                                                          final UUID destinationImplementationId,
                                                          final JsonNode configurationJson)
      throws JsonValidationException, IOException {
    final DestinationConnectionImplementation destinationConnectionImplementation = new DestinationConnectionImplementation()
        .withName(name)
        .withDestinationSpecificationId(destinationSpecificationId)
        .withWorkspaceId(workspaceId)
        .withDestinationImplementationId(destinationImplementationId)
        .withConfiguration(configurationJson);

    configRepository.writeDestinationConnectionImplementation(destinationConnectionImplementation);
  }

  private DestinationImplementationRead buildDestinationImplementationRead(final UUID destinationImplementationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final DestinationConnectionImplementation dci = configRepository.getDestinationConnectionImplementation(destinationImplementationId);

    final UUID destinationId = configRepository.getDestinationConnectionSpecification(dci.getDestinationSpecificationId()).getDestinationId();
    final StandardDestination standardDestination = configRepository.getStandardDestination(destinationId);
    return buildDestinationImplementationRead(dci, standardDestination);
  }

  private DestinationImplementationRead buildDestinationImplementationRead(final DestinationConnectionImplementation destinationConnectionImplementation,
                                                                           final StandardDestination standardDestination) {
    return new DestinationImplementationRead()
        .destinationId(standardDestination.getDestinationId())
        .destinationImplementationId(destinationConnectionImplementation.getDestinationImplementationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationSpecificationId(destinationConnectionImplementation.getDestinationSpecificationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .name(destinationConnectionImplementation.getName())
        .destinationName(standardDestination.getName());
  }

}
