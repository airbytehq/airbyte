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

import io.dataline.api.model.DestinationImplementationCreate;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.DestinationImplementationRead;
import io.dataline.api.model.DestinationImplementationReadList;
import io.dataline.api.model.DestinationImplementationUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import io.dataline.server.helpers.ConfigFetchers;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

public class DestinationImplementationsHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigPersistence configPersistence;
  private final IntegrationSchemaValidation validator;

  public DestinationImplementationsHandler(ConfigPersistence configPersistence,
                                           IntegrationSchemaValidation integrationSchemaValidation,
                                           Supplier<UUID> uuidGenerator) {
    this.configPersistence = configPersistence;
    this.validator = integrationSchemaValidation;
    this.uuidGenerator = uuidGenerator;
  }

  public DestinationImplementationsHandler(ConfigPersistence configPersistence,
                                           IntegrationSchemaValidation integrationSchemaValidation) {
    this(configPersistence, integrationSchemaValidation, UUID::randomUUID);
  }

  public DestinationImplementationRead createDestinationImplementation(DestinationImplementationCreate destinationImplementationCreate) {
    // validate configuration
    validateDestinationImplementation(
        destinationImplementationCreate.getDestinationSpecificationId(),
        (String) destinationImplementationCreate.getConnectionConfiguration());

    // persist
    final UUID destinationImplementationId = uuidGenerator.get();
    persistDestinationConnectionImplementation(
        destinationImplementationCreate.getDestinationSpecificationId(),
        destinationImplementationCreate.getWorkspaceId(),
        destinationImplementationId,
        (String) destinationImplementationCreate.getConnectionConfiguration());

    // read configuration from db
    return getDestinationImplementationInternal(destinationImplementationId);
  }

  public DestinationImplementationRead updateDestinationImplementation(DestinationImplementationUpdate destinationImplementationUpdate) {
    // get existing implementation
    final DestinationImplementationRead persistedDestinationImplementation =
        getDestinationImplementationInternal(
            destinationImplementationUpdate.getDestinationImplementationId());

    // validate configuration
    validateDestinationImplementation(
        persistedDestinationImplementation.getDestinationSpecificationId(),
        (String) destinationImplementationUpdate.getConnectionConfiguration());

    // persist
    persistDestinationConnectionImplementation(
        persistedDestinationImplementation.getDestinationSpecificationId(),
        persistedDestinationImplementation.getWorkspaceId(),
        destinationImplementationUpdate.getDestinationImplementationId(),
        (String) destinationImplementationUpdate.getConnectionConfiguration());

    // read configuration from db
    return getDestinationImplementationInternal(
        destinationImplementationUpdate.getDestinationImplementationId());
  }

  public DestinationImplementationRead getDestinationImplementation(DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {

    return getDestinationImplementationInternal(
        destinationImplementationIdRequestBody.getDestinationImplementationId());
  }

  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {
    final List<DestinationImplementationRead> reads =
        ConfigFetchers.getDestinationConnectionImplementations(configPersistence).stream()
            .filter(
                destinationConnectionImplementation ->
                    destinationConnectionImplementation
                        .getWorkspaceId()
                        .equals(workspaceIdRequestBody.getWorkspaceId()))
            .map(
                destinationConnectionImplementation -> {
                  final UUID destinationId =
                      ConfigFetchers.getDestinationConnectionSpecification(
                              configPersistence,
                              destinationConnectionImplementation.getDestinationSpecificationId())
                          .getDestinationId();
                  return toDestinationImplementationRead(
                      destinationConnectionImplementation, destinationId);
                })
            .collect(Collectors.toList());

    final DestinationImplementationReadList destinationImplementationReadList =
        new DestinationImplementationReadList();
    destinationImplementationReadList.setDestinations(reads);
    return destinationImplementationReadList;
  }

  private DestinationImplementationRead getDestinationImplementationInternal(UUID destinationImplementationId) {
    // read configuration from db
    final DestinationConnectionImplementation retrievedDestinationConnectionImplementation;
    retrievedDestinationConnectionImplementation =
        ConfigFetchers.getDestinationConnectionImplementation(
            configPersistence, destinationImplementationId);

    final UUID destinationId =
        ConfigFetchers.getDestinationConnectionSpecification(
                configPersistence,
                retrievedDestinationConnectionImplementation.getDestinationSpecificationId())
            .getDestinationId();

    return toDestinationImplementationRead(
        retrievedDestinationConnectionImplementation, destinationId);
  }

  private void validateDestinationImplementation(UUID destinationConnectionSpecificationId, String implementationJson) {
    try {
      validator.validateDestinationConnectionConfiguration(          destinationConnectionSpecificationId, implementationJson);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
  }

  private void persistDestinationConnectionImplementation(      UUID destinationSpecificationId,
      UUID workspaceId,
      UUID destinationImplementationId,
      String configurationJson) {
    final DestinationConnectionImplementation destinationConnectionImplementation =
        new DestinationConnectionImplementation();
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfigurationJson(configurationJson);

    ConfigFetchers.writeConfig(
        configPersistence,
        PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplementationId.toString(),
        destinationConnectionImplementation);
  }

  private DestinationImplementationRead toDestinationImplementationRead(      DestinationConnectionImplementation destinationConnectionImplementation, UUID destinationId) {
    final DestinationImplementationRead destinationImplementationRead =
        new DestinationImplementationRead();
    destinationImplementationRead.setDestinationId(destinationId);
    destinationImplementationRead.setDestinationImplementationId(
        destinationConnectionImplementation.getDestinationImplementationId());
    destinationImplementationRead.setWorkspaceId(
        destinationConnectionImplementation.getWorkspaceId());
    destinationImplementationRead.setDestinationSpecificationId(
        destinationConnectionImplementation.getDestinationSpecificationId());
    destinationImplementationRead.setConnectionConfiguration(
        destinationConnectionImplementation.getConfigurationJson());

    return destinationImplementationRead;
  }

}
