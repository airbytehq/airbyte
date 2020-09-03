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

import io.dataline.commons.functional.Factory;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigPersistence;
import java.io.IOException;
import java.util.UUID;

public class SyncJobFactory implements Factory<Long, UUID> {

  private final SchedulerPersistence schedulerPersistence;
  private final ConfigPersistence configPersistence;

  public SyncJobFactory(SchedulerPersistence schedulerPersistence, ConfigPersistence configPersistence) {

    this.schedulerPersistence = schedulerPersistence;
    this.configPersistence = configPersistence;
  }

  public Long create(UUID connectionId) {
    final StandardSync standardSync = ConfigFetchers.getStandardSync(configPersistence, connectionId);

    final SourceConnectionImplementation sourceConnectionImplementation =
        ConfigFetchers.getSourceConnectionImplementation(configPersistence, standardSync.getSourceImplementationId());
    final DestinationConnectionImplementation destinationConnectionImplementation =
        ConfigFetchers.getDestinationConnectionImplementation(configPersistence, standardSync.getDestinationImplementationId());

    try {
      return schedulerPersistence.createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
