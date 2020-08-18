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

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.api.model.CheckConnectionRead;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionSyncRead;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationDiscoverSchemaRead;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardConnectionStatus;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.scheduler.persistence.Job;
import io.dataline.scheduler.persistence.JobStatus;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import io.dataline.server.errors.KnownException;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerHandler {
  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerHandler.class);

  private final ConfigPersistence configPersistence;
  private final SchedulerPersistence schedulerPersistence;

  public SchedulerHandler(
      ConfigPersistence configPersistence, SchedulerPersistence schedulerPersistence) {

    this.configPersistence = configPersistence;
    this.schedulerPersistence = schedulerPersistence;
  }

  public CheckConnectionRead checkSourceImplementationConnection(
      SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    final ObjectMapper objectMapper = new ObjectMapper();

    final SourceConnectionImplementation connectionImplementation;
    try {
      connectionImplementation =
          configPersistence.getConfig(
              PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
              sourceImplementationIdRequestBody.getSourceImplementationId().toString(),
              SourceConnectionImplementation.class);
    } catch (ConfigNotFoundException e) {
      // todo: actually good errors.
      throw new RuntimeException(e);
    } catch (JsonValidationException e) {
      // todo: actually good errors.
      throw new RuntimeException(e);
    }

    final long jobId;
    try {
      jobId =
          schedulerPersistence.createSourceCheckConnectionJob(
              connectionImplementation.getSourceImplementationId(), connectionImplementation);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminal(jobId);

    final StandardConnectionStatus connectionStatus =
        job.getOutput()
            .orElseThrow(() -> new RuntimeException("Terminal job does not have an output"))
            .getCheckConnection();

    final CheckConnectionRead checkConnectionRead = new CheckConnectionRead();

    checkConnectionRead.setStatus(
        Enums.convertTo(connectionStatus.getStatus(), CheckConnectionRead.StatusEnum.class));
    checkConnectionRead.setMessage(connectionStatus.getMessage());

    return checkConnectionRead;
  }

  private Job waitUntilJobIsTerminal(long jobId) {
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

      if (count > 10) {
        throw new RuntimeException("Check connection job did not complete.");
      }

      count++;

      try {
        Thread.sleep(500);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  public CheckConnectionRead checkDestinationImplementationConnection(
      DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }

  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(
      SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }

  public ConnectionSyncRead syncConnection(ConnectionIdRequestBody connectionIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }
}
