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

package io.dataline.scheduler;

import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import java.io.IOException;
import java.util.List;
import java.util.UUID;

// todo (cgardens) - deduplicate this with the ConfigFetchers in dataline-server. requires creating
// a class that takes in an exception provider. also requires figuring out the dependency DAG to
// avoid circular dependency issues.
/**
 * These helpers catch exceptions thrown in the config persistence and throws them as
 * RuntimeExceptions
 */
public class ConfigFetchers {

  public static SourceConnectionImplementation getSourceConnectionImplementation(ConfigPersistence configPersistence,
                                                                                 UUID sourceImplementationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
          sourceImplementationId.toString(),
          SourceConnectionImplementation.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getJsonInvalidException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static DestinationConnectionImplementation getDestinationConnectionImplementation(ConfigPersistence configPersistence,
                                                                                           UUID destinationImplementationId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.DESTINATION_CONNECTION_IMPLEMENTATION,
          destinationImplementationId.toString(),
          DestinationConnectionImplementation.class);
    } catch (JsonValidationException e) {
      throw getJsonInvalidException(e);
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
          PersistenceConfigType.STANDARD_SYNC,
          connectionId.toString(),
          StandardSync.class);
    } catch (JsonValidationException e) {
      throw getJsonInvalidException(e);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<StandardSync> getStandardSyncs(ConfigPersistence configPersistence) {
    try {
      return configPersistence.listConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getJsonInvalidException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardSyncSchedule getStandardSyncSchedule(ConfigPersistence configPersistence,
                                                             UUID connectionId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
          connectionId.toString(),
          StandardSyncSchedule.class);
    } catch (ConfigNotFoundException e) {
      throw getConfigNotFoundException(e);
    } catch (JsonValidationException e) {
      throw getJsonInvalidException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static RuntimeException getConfigNotFoundException(ConfigNotFoundException e) {
    return new RuntimeException(
        String.format("Could not find sync configuration for %s: %s.", e.getType().toString(), e.getConfigId()), e);
  }

  private static RuntimeException getJsonInvalidException(Throwable e) {
    return new RuntimeException(
        String.format(
            "The provided configuration does not fulfill the specification. Errors: %s",
            e.getMessage()),
        e);
  }

}
