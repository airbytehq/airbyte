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

package io.airbyte.config.persistence;

import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.SourceConnectionSpecification;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.StandardSource;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.StandardWorkspace;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigRepository {

  private final static Logger LOGGER = LoggerFactory.getLogger(ConfigRepository.class);

  private final ConfigPersistence persistence;

  public ConfigRepository(ConfigPersistence persistence) {
    this.persistence = persistence;
  }

  public StandardWorkspace getStandardWorkspace(final UUID workspaceId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_WORKSPACE,
        workspaceId.toString(),
        StandardWorkspace.class);
  }

  public void writeStandardWorkspace(final StandardWorkspace workspace)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.STANDARD_WORKSPACE,
        workspace.getWorkspaceId().toString(),
        workspace);
  }

  public StandardSource getStandardSource(final UUID sourceId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_SOURCE, sourceId.toString(), StandardSource.class);
  }

  public List<StandardSource> listStandardSources()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SOURCE, StandardSource.class);
  }

  public StandardDestination getStandardDestination(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_DESTINATION,
        destinationId.toString(),
        StandardDestination.class);
  }

  public List<StandardDestination> listStandardDestinations()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(ConfigSchema.STANDARD_DESTINATION, StandardDestination.class);
  }

  public SourceConnectionSpecification getSourceConnectionSpecification(final UUID sourceSpecificationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        sourceSpecificationId.toString(),
        SourceConnectionSpecification.class);
  }

  public SourceConnectionSpecification getSourceConnectionSpecificationFromSourceId(final UUID sourceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // since we are not querying on a the primary key, we have to list all of the specification objects
    // and then
    // filter.
    return listSourceConnectionSpecifications().stream()
        .filter(s -> s.getSourceId().equals(sourceId))
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION_SPECIFICATION, sourceId.toString()));
  }

  public DestinationConnectionSpecification getDestinationConnectionSpecificationFromDestinationId(final UUID destinationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return listDestinationConnectionSpecifications().stream()
        .filter(d -> d.getDestinationId().equals(destinationId))
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION, destinationId.toString()));
  }

  public List<SourceConnectionSpecification> listSourceConnectionSpecifications()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(
        ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
        SourceConnectionSpecification.class);
  }

  public DestinationConnectionSpecification getDestinationConnectionSpecification(final UUID destinationSpecificationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION,
        destinationSpecificationId.toString(),
        DestinationConnectionSpecification.class);
  }

  public List<DestinationConnectionSpecification> listDestinationConnectionSpecifications()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(
        ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION,
        DestinationConnectionSpecification.class);
  }

  public SourceConnectionImplementation getSourceConnectionImplementation(final UUID sourceImplementationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        SourceConnectionImplementation.class);
  }

  public void writeSourceConnectionImplementation(final SourceConnectionImplementation sourceImplementation)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementation.getSourceImplementationId().toString(),
        sourceImplementation);
  }

  public List<SourceConnectionImplementation> listSourceConnectionImplementations()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        SourceConnectionImplementation.class);
  }

  public DestinationConnectionImplementation getDestinationConnectionImplementation(final UUID destinationImplementationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplementationId.toString(),
        DestinationConnectionImplementation.class);
  }

  public void writeDestinationConnectionImplementation(DestinationConnectionImplementation destinationConnectionImplementation)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationConnectionImplementation.getDestinationImplementationId().toString(),
        destinationConnectionImplementation);
  }

  public List<DestinationConnectionImplementation> listDestinationConnectionImplementations()
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.listConfigs(
        ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
        DestinationConnectionImplementation.class);
  }

  public StandardSync getStandardSync(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_SYNC,
        connectionId.toString(),
        StandardSync.class);
  }

  public void writeStandardSync(final StandardSync standardSync)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.STANDARD_SYNC,
        standardSync.getConnectionId().toString(),
        standardSync);
  }

  public List<StandardSync> listStandardSyncs()
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
  }

  public StandardSyncSchedule getStandardSyncSchedule(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_SYNC_SCHEDULE,
        connectionId.toString(),
        StandardSyncSchedule.class);
  }

  public void writeStandardSchedule(final StandardSyncSchedule schedule)
      throws JsonValidationException, IOException {
    // todo (cgardens) - stored on sync id (there is no schedule id concept). this is non-intuitive.
    persistence.writeConfig(
        ConfigSchema.STANDARD_SYNC_SCHEDULE,
        schedule.getConnectionId().toString(),
        schedule);
  }

}
