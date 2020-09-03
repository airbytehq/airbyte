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

import io.dataline.api.model.CheckConnectionRead;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionSyncRead;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationDiscoverSchemaRead;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.scheduler.SchedulerPersistence;
import io.dataline.server.converters.SchemaConverter;
import io.dataline.server.helpers.ConfigFetchers;
import java.io.IOException;
import java.util.UUID;
import javax.validation.constraints.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerHandler.class);

  private final ConfigPersistence configPersistence;
  private final SchedulerPersistence schedulerPersistence;

  public SchedulerHandler(ConfigPersistence configPersistence,
                          SchedulerPersistence schedulerPersistence) {

    this.configPersistence = configPersistence;
    this.schedulerPersistence = schedulerPersistence;
  }

  public CheckConnectionRead checkSourceImplementationConnection(SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {

    final SourceConnectionImplementation connectionImplementation =
        ConfigFetchers.getSourceConnectionImplementation(
            configPersistence, sourceImplementationIdRequestBody.getSourceImplementationId());

    final long jobId;
    try {
      jobId = schedulerPersistence.createSourceCheckConnectionJob(connectionImplementation);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);
    return reportConnectionStatus(job);
  }

  public CheckConnectionRead checkDestinationImplementationConnection(DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {

    final DestinationConnectionImplementation connectionImplementation =
        ConfigFetchers.getDestinationConnectionImplementation(
            configPersistence,
            destinationImplementationIdRequestBody.getDestinationImplementationId());

    final long jobId;
    try {
      jobId = schedulerPersistence.createDestinationCheckConnectionJob(connectionImplementation);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);
    return reportConnectionStatus(job);
  }

  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    final SourceConnectionImplementation connectionImplementation =
        ConfigFetchers.getSourceConnectionImplementation(
            configPersistence, sourceImplementationIdRequestBody.getSourceImplementationId());

    final long jobId;
    try {
      jobId = schedulerPersistence.createDiscoverSchemaJob(connectionImplementation);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    final StandardDiscoverSchemaOutput output =
        job.getOutput()
            .orElseThrow(() -> new RuntimeException("Terminal job does not have an output"))
            .getDiscoverSchema();

    LOGGER.info("output = " + output);

    final SourceImplementationDiscoverSchemaRead read =
        new SourceImplementationDiscoverSchemaRead();
    read.setSchema(SchemaConverter.toApiSchema(output.getSchema()));

    return read;
  }

  public ConnectionSyncRead syncConnection(ConnectionIdRequestBody connectionIdRequestBody) {
    @NotNull
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync;
    standardSync = ConfigFetchers.getStandardSync(configPersistence, connectionId);

    final SourceConnectionImplementation sourceConnectionImplementation =
        ConfigFetchers.getSourceConnectionImplementation(
            configPersistence, standardSync.getSourceImplementationId());
    final DestinationConnectionImplementation destinationConnectionImplementation =
        ConfigFetchers.getDestinationConnectionImplementation(
            configPersistence, standardSync.getDestinationImplementationId());

    final long jobId;
    try {
      jobId =
          schedulerPersistence.createSyncJob(
              sourceConnectionImplementation, destinationConnectionImplementation, standardSync);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    final ConnectionSyncRead read = new ConnectionSyncRead();
    read.setStatus(
        job.getStatus().equals(JobStatus.COMPLETED)
            ? ConnectionSyncRead.StatusEnum.SUCCESS
            : ConnectionSyncRead.StatusEnum.FAIL);

    return read;
  }

  private Job waitUntilJobIsTerminalOrTimeout(long jobId) {
    int count = 0;
    while (true) {
      final Job job;
      try {
        job = schedulerPersistence.getJob(jobId);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }

      if (JobStatus.TERMINAL_STATUSES.contains(job.getStatus())) {
        return job;
      }

      if (count > 120) {
        throw new RuntimeException("Check connection job did not complete.");
      }

      count++;

      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  private CheckConnectionRead reportConnectionStatus(Job job) {
    final StandardCheckConnectionOutput output =
        job.getOutput()
            .orElseThrow(() -> new RuntimeException("Terminal job does not have an output"))
            .getCheckConnection();

    final CheckConnectionRead checkConnectionRead = new CheckConnectionRead();

    checkConnectionRead.setStatus(
        Enums.convertTo(output.getStatus(), CheckConnectionRead.StatusEnum.class));
    checkConnectionRead.setMessage(output.getMessage());

    return checkConnectionRead;
  }

}
