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

package io.dataline.server.helpers;

import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.DestinationConnectionSpecification;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.SourceConnectionSpecification;
import io.dataline.config.StandardDestination;
import io.dataline.config.StandardSource;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
import java.util.Set;
import java.util.UUID;

public class ConfigFetchers {

  public static StandardWorkspace getStandardWorkspace(
      ConfigPersistence configPersistence, UUID workspaceId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_WORKSPACE,
          workspaceId.toString(),
          StandardWorkspace.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "standardWorkspace", workspaceId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static StandardSource getStandardSource(
      ConfigPersistence configPersistence, UUID sourceId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SOURCE, sourceId.toString(), StandardSource.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "standardSource", sourceId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static Set<StandardSource> getStandardSources(ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.STANDARD_SOURCE, StandardSource.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static SourceConnectionSpecification getSourceConnectionSpecification(
      ConfigPersistence configPersistence, UUID sourceSpecificationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
          sourceSpecificationId.toString(),
          SourceConnectionSpecification.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "sourceConnectionSpecification", sourceSpecificationId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static Set<SourceConnectionSpecification> getSourceConnectionSpecifications(
      ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.SOURCE_CONNECTION_SPECIFICATION,
          SourceConnectionSpecification.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static SourceConnectionImplementation getSourceConnectionImplementation(
      ConfigPersistence configPersistence, UUID sourceImplementationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
          sourceImplementationId.toString(),
          SourceConnectionImplementation.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "sourceConnectionImplementation", sourceImplementationId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static Set<SourceConnectionImplementation> getSourceConnectionImplementations(
      ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
          SourceConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static StandardDestination getStandardDestination(
      ConfigPersistence configPersistence, UUID destinationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_DESTINATION,
          destinationId.toString(),
          StandardDestination.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "standardDestination", destinationId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static Set<StandardDestination> getStandardDestinations(
      ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.STANDARD_DESTINATION, StandardDestination.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static DestinationConnectionSpecification getDestinationConnectionSpecification(
      ConfigPersistence configPersistence, UUID destinationSpecificationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
          destinationSpecificationId.toString(),
          DestinationConnectionSpecification.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(
          e, "destinationConnectionSpecification", destinationSpecificationId);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static Set<DestinationConnectionSpecification> getDestinationConnectionSpecifications(
      ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.DESTINATION_CONNECTION_SPECIFICATION,
          DestinationConnectionSpecification.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static DestinationConnectionImplementation getDestinationConnectionImplementation(
      ConfigPersistence configPersistence, UUID destinationImplementationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
          destinationImplementationId.toString(),
          DestinationConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(
          e, "destinationConnectionImplementation", destinationImplementationId);
    }
  }

  public static Set<DestinationConnectionImplementation> getDestinationConnectionImplementations(
      ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(
          PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
          DestinationConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static StandardSync getStandardSync(
      ConfigPersistence configPersistence, UUID connectionId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "connection", connectionId);
    }
  }

  public static Set<StandardSync> getStandardSyncs(ConfigPersistence configPersistence) {
    try {
      return configPersistence.getConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    }
  }

  public static StandardSyncSchedule getStandardSyncSchedule(
      ConfigPersistence configPersistence, UUID connectionId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
          connectionId.toString(),
          StandardSyncSchedule.class);
    } catch (JsonValidationException e) {
      throw getInvalidException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e, "syncSchedule", connectionId);
    }
  }

  private static KnownException getConfigNotFoundException(
      Throwable e, String configName, UUID id) {
    return new KnownException(
        422, String.format("Could not find sync configuration for %s: %s.", configName, id), e);
  }

  private static KnownException getInvalidException(Throwable e) {
    return new KnownException(
        422,
        String.format(
            "The provided configuration does not fulfill the specification. Errors: %s",
            e.getMessage()),
        e);
  }
}
