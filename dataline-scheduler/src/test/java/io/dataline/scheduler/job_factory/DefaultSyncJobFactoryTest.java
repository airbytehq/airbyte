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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.dataline.config.ConfigSchema;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DefaultSyncJobFactoryTest {

  @Test
  void createSyncJobFromConnectionId() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID connectionId = UUID.randomUUID();
    final UUID sourceImplId = UUID.randomUUID();
    final UUID destinationImplId = UUID.randomUUID();
    final SchedulerPersistence schedulerPersistence = mock(SchedulerPersistence.class);
    final ConfigPersistence configPersistence = mock(ConfigPersistence.class);
    final long jobId = 11L;

    final StandardSync standardSync = new StandardSync();
    standardSync.setSourceImplementationId(sourceImplId);
    standardSync.setDestinationImplementationId(destinationImplId);

    final SourceConnectionImplementation sourceConnectionImplementation = new SourceConnectionImplementation();
    final DestinationConnectionImplementation destinationConnectionImplementation = new DestinationConnectionImplementation();

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_SYNC,
        connectionId.toString(),
        StandardSync.class)).thenReturn(standardSync);
    when(configPersistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplId.toString(),
        SourceConnectionImplementation.class)).thenReturn(sourceConnectionImplementation);
    when(configPersistence.getConfig(
        ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplId.toString(),
        DestinationConnectionImplementation.class)).thenReturn(destinationConnectionImplementation);
    when(schedulerPersistence.createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync)).thenReturn(jobId);

    final SyncJobFactory factory = new DefaultSyncJobFactory(schedulerPersistence, configPersistence);
    final long actualJobId = factory.create(connectionId);
    assertEquals(jobId, actualJobId);

    verify(configPersistence).getConfig(ConfigSchema.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
    verify(configPersistence)
        .getConfig(
            ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceImplId.toString(),
            SourceConnectionImplementation.class);
    verify(configPersistence)
        .getConfig(
            ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
            destinationImplId.toString(),
            DestinationConnectionImplementation.class);
    verify(schedulerPersistence).createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync);
  }

}
