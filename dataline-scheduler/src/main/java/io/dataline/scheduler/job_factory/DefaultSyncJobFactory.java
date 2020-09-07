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

package io.dataline.scheduler.job_factory;

import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.util.UUID;

public class DefaultSyncJobFactory implements SyncJobFactory {

  private final SchedulerPersistence schedulerPersistence;
  private final ConfigRepository configRepository;

  public DefaultSyncJobFactory(final SchedulerPersistence schedulerPersistence,
                               final ConfigRepository configRepository) {

    this.schedulerPersistence = schedulerPersistence;
    this.configRepository = configRepository;
  }

  public Long create(final UUID connectionId) {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);

      return schedulerPersistence.createSyncJob(
          configRepository.getSourceConnectionImplementation(standardSync.getSourceImplementationId()),
          configRepository.getDestinationConnectionImplementation(standardSync.getDestinationImplementationId()),
          standardSync);
    } catch (IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

}
