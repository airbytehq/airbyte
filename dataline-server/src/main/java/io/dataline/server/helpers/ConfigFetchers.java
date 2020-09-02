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

import io.dataline.config.ConfigSchema;
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
import io.dataline.server.errors.KnownException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;

/**
 * These helpers catch exceptions thrown in the config persistence and throws them as
 * KnownExceptions that can be processed by the server and returned to the user in human-readable
 * form.
 */
public class ConfigFetchers {

  public static StandardWorkspace getStandardWorkspace(ConfigPersistence configPersistence,
                                                       UUID workspaceId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.STANDARD_WORKSPACE,
          workspaceId.toString(),
          StandardWorkspace.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardSource getStandardSource(ConfigPersistence configPersistence,
                                                 UUID sourceId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.STANDARD_SOURCE, sourceId.toString(), StandardSource.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  // wrap json validation errors for usages in API handlers.
  public static <T> void writeConfig(ConfigPersistence configPersistence,
                                     ConfigSchema configType,
                                     String configId,
                                     T config) {
    try {
      configPersistence.writeConfig(configType, configId, config);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<StandardSource> getStandardSources(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE, StandardSource.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static SourceConnectionSpecification getSourceConnectionSpecification(ConfigPersistence configPersistence,
                                                                               UUID sourceSpecificationId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
          sourceSpecificationId.toString(),
          SourceConnectionSpecification.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<SourceConnectionSpecification> getSourceConnectionSpecifications(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(
          ConfigSchema.SOURCE_CONNECTION_SPECIFICATION,
          SourceConnectionSpecification.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static SourceConnectionImplementation getSourceConnectionImplementation(ConfigPersistence configPersistence,
                                                                                 UUID sourceImplementationId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
          sourceImplementationId.toString(),
          SourceConnectionImplementation.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<SourceConnectionImplementation> getSourceConnectionImplementations(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(
          ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
          SourceConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardDestination getStandardDestination(ConfigPersistence configPersistence,
                                                           UUID destinationId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.STANDARD_DESTINATION,
          destinationId.toString(),
          StandardDestination.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<StandardDestination> getStandardDestinations(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION, StandardDestination.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static DestinationConnectionSpecification getDestinationConnectionSpecification(ConfigPersistence configPersistence,
                                                                                         UUID destinationSpecificationId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION,
          destinationSpecificationId.toString(),
          DestinationConnectionSpecification.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<DestinationConnectionSpecification> getDestinationConnectionSpecifications(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(
          ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION,
          DestinationConnectionSpecification.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static DestinationConnectionImplementation getDestinationConnectionImplementation(ConfigPersistence configPersistence,
                                                                                           UUID destinationImplementationId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
          destinationImplementationId.toString(),
          DestinationConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<DestinationConnectionImplementation> getDestinationConnectionImplementations(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(
          ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
          DestinationConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardSync getStandardSync(ConfigPersistence configPersistence,
                                             UUID connectionId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<StandardSync> getStandardSyncs(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardSyncSchedule getStandardSyncSchedule(ConfigPersistence configPersistence,
                                                             UUID connectionId) {
    try {
      return configPersistence.getConfig(
          ConfigSchema.STANDARD_SYNC_SCHEDULE,
          connectionId.toString(),
          StandardSyncSchedule.class);
    } catch (JsonValidationException e) {
      throw getInvalidJsonException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static KnownException getConfigNotFoundException(ConfigNotFoundException e) {
    return new KnownException(
        422, String.format("Could not find sync configuration for %s: %s.", e.getType().toString(), e.getConfigId()), e);
  }

  private static KnownException getInvalidJsonException(Throwable e) {
    return new KnownException(
        422,
        String.format(
            "The provided configuration does not fulfill the specification. Errors: %s",
            e.getMessage()),
        e);
  }

}
