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
import java.util.Set;
import java.util.UUID;

/**
 * These helpers catch exceptions thrown in the config persistence and throws them as
 * RuntimeExceptions
 */
public class ConfigFetchers {

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

  private static RuntimeException getConfigNotFoundException(
      Throwable e, String configName, UUID id) {
    return new RuntimeException(
        String.format("Could not find sync configuration for %s: %s.", configName, id), e);
  }

  private static RuntimeException getInvalidException(Throwable e) {
    return new RuntimeException(
        String.format(
            "The provided configuration does not fulfill the specification. Errors: %s",
            e.getMessage()),
        e);
  }
}
