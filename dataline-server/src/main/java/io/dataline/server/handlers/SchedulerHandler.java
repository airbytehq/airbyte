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

import com.google.common.collect.ImmutableMap;
import io.dataline.analytics.TrackingClientSingleton;
import io.dataline.api.model.CheckConnectionRead;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionSyncRead;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationDiscoverSchemaRead;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobOutput;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.commons.json.JsonValidationException;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import io.dataline.server.converters.SchemaConverter;
import java.io.IOException;
import java.util.Collections;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerHandler.class);

  private final ConfigRepository configRepository;
  private final SchedulerPersistence schedulerPersistence;

  public SchedulerHandler(final ConfigRepository configRepository,
                          final SchedulerPersistence schedulerPersistence) {

    this.configRepository = configRepository;
    this.schedulerPersistence = schedulerPersistence;
  }

  public CheckConnectionRead checkSourceImplementationConnection(SourceImplementationIdRequestBody sourceImplementationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnectionImplementation connectionImplementation =
        configRepository.getSourceConnectionImplementation(sourceImplementationIdRequestBody.getSourceImplementationId());

    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(connectionImplementation);
    LOGGER.debug("jobId = " + jobId);
    final CheckConnectionRead checkConnectionRead = reportConnectionStatus(waitUntilJobIsTerminalOrTimeout(jobId));

    TrackingClientSingleton.get().track("check_connection", ImmutableMap.<String, Object>builder()
        .put("type", "source")
        .put("name", connectionImplementation.getName())
        .put("source_specification_id", connectionImplementation.getSourceSpecificationId())
        .put("source_implementation_id", connectionImplementation.getSourceImplementationId())
        .put("check_connection_result", checkConnectionRead.getStatus())
        .put("job_id", jobId)
        .build());

    return checkConnectionRead;
  }

  public CheckConnectionRead checkDestinationImplementationConnection(DestinationImplementationIdRequestBody destinationImplementationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationConnectionImplementation connectionImplementation =
        configRepository.getDestinationConnectionImplementation(destinationImplementationIdRequestBody.getDestinationImplementationId());

    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(connectionImplementation);
    LOGGER.debug("jobId = " + jobId);
    final CheckConnectionRead checkConnectionRead = reportConnectionStatus(waitUntilJobIsTerminalOrTimeout(jobId));

    TrackingClientSingleton.get().track("check_connection", ImmutableMap.<String, Object>builder()
        .put("type", "destination")
        .put("name", connectionImplementation.getName())
        .put("destination_specification_id", connectionImplementation.getDestinationSpecificationId())
        .put("destination_implementation_id", connectionImplementation.getDestinationImplementationId())
        .put("check_connection_result", checkConnectionRead.getStatus())
        .put("job_id", jobId)
        .build());

    return checkConnectionRead;
  }

  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(SourceImplementationIdRequestBody sourceImplementationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnectionImplementation connectionImplementation =
        configRepository.getSourceConnectionImplementation(sourceImplementationIdRequestBody.getSourceImplementationId());

    final long jobId = schedulerPersistence.createDiscoverSchemaJob(connectionImplementation);
    LOGGER.debug("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    final StandardDiscoverSchemaOutput output = job.getOutput().map(JobOutput::getDiscoverSchema)
        // the job should always produce an output, but if does not, we fall back on an empty schema.
        .orElse(new StandardDiscoverSchemaOutput().withSchema(new Schema().withTables(Collections.emptyList())));

    LOGGER.debug("output = " + output);

    TrackingClientSingleton.get().track("discover_schema", ImmutableMap.<String, Object>builder()
        .put("name", connectionImplementation.getName())
        .put("source_specification_id", connectionImplementation.getSourceSpecificationId())
        .put("source_implementation_id", connectionImplementation.getSourceImplementationId())
        .put("job_id", jobId)
        .build());

    return new SourceImplementationDiscoverSchemaRead().schema(SchemaConverter.toApiSchema(output.getSchema()));
  }

  public ConnectionSyncRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final SourceConnectionImplementation sourceConnectionImplementation =
        configRepository.getSourceConnectionImplementation(standardSync.getSourceImplementationId());
    final DestinationConnectionImplementation destinationConnectionImplementation =
        configRepository.getDestinationConnectionImplementation(standardSync.getDestinationImplementationId());

    final long jobId = schedulerPersistence.createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    TrackingClientSingleton.get().track("sync", ImmutableMap.<String, Object>builder()
        .put("name", standardSync.getName())
        .put("connection_id", standardSync.getConnectionId())
        .put("sync_mode", standardSync.getSyncMode())
        .put("source_specification_id", sourceConnectionImplementation.getSourceSpecificationId())
        .put("source_implementation_id", sourceConnectionImplementation.getSourceImplementationId())
        .put("destination_specification_id", destinationConnectionImplementation.getDestinationSpecificationId())
        .put("destination_implementation_id", destinationConnectionImplementation.getDestinationImplementationId())
        .put("job_id", jobId)
        .build());

    return new ConnectionSyncRead()
        .status(job.getStatus().equals(JobStatus.COMPLETED) ? ConnectionSyncRead.StatusEnum.SUCCESS : ConnectionSyncRead.StatusEnum.FAIL);
  }

  private Job waitUntilJobIsTerminalOrTimeout(final long jobId) throws IOException {
    for (int i = 0; i < 120; i++) {
      final Job job = schedulerPersistence.getJob(jobId);

      if (JobStatus.TERMINAL_STATUSES.contains(job.getStatus())) {
        return job;
      }

      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }

    throw new RuntimeException("Check connection job did not complete.");
  }

  private CheckConnectionRead reportConnectionStatus(final Job job) {
    final StandardCheckConnectionOutput output = job.getOutput().map(JobOutput::getCheckConnection)
        // the job should always produce an output, but if it does not, we assume a failure.
        .orElse(new StandardCheckConnectionOutput().withStatus(StandardCheckConnectionOutput.Status.FAILURE));

    return new CheckConnectionRead()
        .status(Enums.convertTo(output.getStatus(), CheckConnectionRead.StatusEnum.class))
        .message(output.getMessage());
  }

}
