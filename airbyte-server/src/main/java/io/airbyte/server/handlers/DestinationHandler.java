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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class DestinationHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SchedulerHandler schedulerHandler;
  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;

  public DestinationHandler(final ConfigRepository configRepository,
                            final JsonSchemaValidator integrationSchemaValidation,
                            final SchedulerHandler schedulerHandler,
                            final ConnectionsHandler connectionsHandler,
                            final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.validator = integrationSchemaValidation;
    this.schedulerHandler = schedulerHandler;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
  }

  public DestinationHandler(final ConfigRepository configRepository,
                            final JsonSchemaValidator integrationSchemaValidation,
                            final SchedulerHandler schedulerHandler,
                            final ConnectionsHandler connectionsHandler) {
    this(configRepository, integrationSchemaValidation, schedulerHandler, connectionsHandler, UUID::randomUUID);
  }

  public DestinationRead createDestination(final DestinationCreate destinationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    validateDestination(
        destinationCreate.getDestinationDefinitionId(),
        destinationCreate.getConnectionConfiguration());

    // persist
    final UUID destinationId = uuidGenerator.get();
    persistDestinationConnection(
        destinationCreate.getName() != null ? destinationCreate.getName() : "default",
        destinationCreate.getDestinationDefinitionId(),
        destinationCreate.getWorkspaceId(),
        destinationId,
        destinationCreate.getConnectionConfiguration(),
        false);

    // read configuration from db
    return buildDestinationRead(destinationId);
  }

  public void deleteDestination(final DestinationIdRequestBody destinationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing implementation
    final DestinationRead destinationImpl =
        buildDestinationRead(destinationIdRequestBody.getDestinationId());

    // disable all connections associated with this destinationImplemenation
    // Delete connections first in case it it fails in the middle, destination will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(destinationImpl.getWorkspaceId());
    for (ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getDestinationId().equals(destinationImpl.getDestinationId())) {
        continue;
      }

      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .connectionId(connectionRead.getConnectionId())
          .syncSchema(connectionRead.getSyncSchema())
          .schedule(connectionRead.getSchedule())
          .status(ConnectionStatus.DEPRECATED);

      connectionsHandler.updateConnection(connectionUpdate);
    }

    // persist
    persistDestinationConnection(
        destinationImpl.getName(),
        destinationImpl.getDestinationDefinitionId(),
        destinationImpl.getWorkspaceId(),
        destinationImpl.getDestinationId(),
        destinationImpl.getConnectionConfiguration(),
        true);
  }

  public DestinationRead updateDestination(final DestinationUpdate destinationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing implementation
    final DestinationConnectionImplementation currentDci =
        configRepository.getDestinationConnectionImplementation(destinationUpdate.getDestinationId());

    // validate configuration
    validateDestination(
        currentDci.getDestinationId(),
        destinationUpdate.getConnectionConfiguration());

    // persist
    persistDestinationConnection(
        destinationUpdate.getName(),
        currentDci.getDestinationId(),
        currentDci.getWorkspaceId(),
        destinationUpdate.getDestinationId(),
        destinationUpdate.getConnectionConfiguration(),
        currentDci.getTombstone());

    // read configuration from db
    return buildDestinationRead(destinationUpdate.getDestinationId());
  }

  public DestinationRead getDestination(DestinationIdRequestBody destinationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildDestinationRead(destinationIdRequestBody.getDestinationId());
  }

  public DestinationReadList listDestinationsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationRead> reads = Lists.newArrayList();

    for (DestinationConnectionImplementation dci : configRepository.listDestinationConnectionImplementations()) {
      if (!dci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }

      if (dci.getTombstone()) {
        continue;
      }

      reads.add(buildDestinationRead(dci.getDestinationImplementationId()));
    }

    return new DestinationReadList().destinations(reads);
  }

  private void validateDestination(final UUID destinationId,
                                   final JsonNode implementationJson)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    DestinationDefinitionSpecificationRead dcs =
        schedulerHandler.getDestinationSpecification(new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationId));
    validator.validate(dcs.getConnectionSpecification(), implementationJson);
  }

  private void persistDestinationConnection(final String name,
                                            final UUID destinationDefinitionId,
                                            final UUID workspaceId,
                                            final UUID destinationId,
                                            final JsonNode configurationJson,
                                            final boolean tombstone)
      throws JsonValidationException, IOException {
    final DestinationConnectionImplementation destinationConnectionImplementation = new DestinationConnectionImplementation()
        .withName(name)
        .withDestinationId(destinationDefinitionId)
        .withWorkspaceId(workspaceId)
        .withDestinationImplementationId(destinationId)
        .withConfiguration(configurationJson)
        .withTombstone(tombstone);

    configRepository.writeDestinationConnectionImplementation(destinationConnectionImplementation);
  }

  private DestinationRead buildDestinationRead(final UUID destinationImplementationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final DestinationConnectionImplementation dci = configRepository.getDestinationConnectionImplementation(destinationImplementationId);
    final StandardDestination standardDestination = configRepository.getStandardDestination(dci.getDestinationId());
    return buildDestinationRead(dci, standardDestination);
  }

  private DestinationRead buildDestinationRead(final DestinationConnectionImplementation destinationConnectionImplementation,
                                               final StandardDestination standardDestination) {
    return new DestinationRead()
        .destinationDefinitionId(standardDestination.getDestinationId())
        .destinationId(destinationConnectionImplementation.getDestinationImplementationId())
        .workspaceId(destinationConnectionImplementation.getWorkspaceId())
        .destinationDefinitionId(destinationConnectionImplementation.getDestinationId())
        .connectionConfiguration(destinationConnectionImplementation.getConfiguration())
        .name(destinationConnectionImplementation.getName())
        .destinationName(standardDestination.getName());
  }

}
