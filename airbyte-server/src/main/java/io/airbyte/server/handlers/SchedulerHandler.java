/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.server.handlers;

import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionSyncRead;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.AirbyteProtocolConverters;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobOutput;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import io.airbyte.server.converters.SchemaConverter;
import io.airbyte.validation.json.JsonValidationException;
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

  public CheckConnectionRead checkSourceConnection(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection connectionImplementation =
        configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());

    final StandardSourceDefinition source = configRepository.getStandardSourceDefinition(connectionImplementation.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(connectionImplementation, imageName);
    LOGGER.debug("jobId = " + jobId);
    final CheckConnectionRead checkConnectionRead = reportConnectionStatus(waitUntilJobIsTerminalOrTimeout(jobId));

    TrackingClientSingleton.get().track("check_connection", ImmutableMap.<String, Object>builder()
        .put("type", "source")
        .put("name", connectionImplementation.getName())
        .put("source_id", connectionImplementation.getSourceDefinitionId())
        .put("source_implementation_id", connectionImplementation.getSourceId())
        .put("check_connection_result", checkConnectionRead.getStatus())
        .put("job_id", jobId)
        .build());

    return checkConnectionRead;
  }

  public CheckConnectionRead checkDestinationConnection(DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationConnection connectionImplementation =
        configRepository.getDestinationConnection(destinationIdRequestBody.getDestinationId());

    final StandardDestinationDefinition destination =
        configRepository.getStandardDestinationDefinition(connectionImplementation.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());
    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(connectionImplementation, imageName);
    LOGGER.debug("jobId = " + jobId);
    final CheckConnectionRead checkConnectionRead = reportConnectionStatus(waitUntilJobIsTerminalOrTimeout(jobId));

    TrackingClientSingleton.get().track("check_connection", ImmutableMap.<String, Object>builder()
        .put("type", "destination")
        .put("name", connectionImplementation.getName())
        .put("destination_implementation_id", connectionImplementation.getDestinationId())
        .put("destination_id", connectionImplementation.getDestinationDefinitionId())
        .put("check_connection_result", checkConnectionRead.getStatus())
        .put("job_id", jobId)
        .build());

    return checkConnectionRead;
  }

  public SourceDiscoverSchemaRead discoverSchemaForSource(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection connectionImplementation =
        configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());

    StandardSourceDefinition source = configRepository.getStandardSourceDefinition(connectionImplementation.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
    final long jobId = schedulerPersistence.createDiscoverSchemaJob(connectionImplementation, imageName);
    LOGGER.debug("jobId = " + jobId);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    final Schema schema = job.getOutput()
        .map(out -> AirbyteProtocolConverters.toSchema(out.getDiscoverCatalog().getCatalog()))
        // the job should always produce an output, but if does not, we fall back on an empty schema.
        .orElse(new Schema().withStreams(Collections.emptyList()));

    LOGGER.debug("schema = " + schema);

    TrackingClientSingleton.get().track("discover_schema", ImmutableMap.<String, Object>builder()
        .put("name", connectionImplementation.getName())
        .put("source_id", connectionImplementation.getSourceDefinitionId())
        .put("source_implementation_id", connectionImplementation.getSourceId())
        .put("job_id", jobId)
        .build());

    return new SourceDiscoverSchemaRead().schema(SchemaConverter.toApiSchema(schema));
  }

  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    UUID sourceDefinitionId = sourceDefinitionIdRequestBody.getSourceDefinitionId();
    StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final String imageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
    final ConnectorSpecification spec = getConnectorSpecification(imageName);

    TrackingClientSingleton.get().track("get_source_spec", ImmutableMap.<String, Object>builder()
        .put("source_id", source.getSourceDefinitionId())
        .put("source_name", source.getName())
        .put("image_name", imageName)
        .build());

    return new SourceDefinitionSpecificationRead()
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .sourceDefinitionId(sourceDefinitionId);
  }

  public ConnectorSpecification getConnectorSpecification(String imageName) throws IOException {
    final long jobId = schedulerPersistence.createGetSpecJob(imageName);
    LOGGER.debug("getSourceSpec jobId = {}", jobId);

    Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    return job.getOutput().orElseThrow().getGetSpec().getSpecification();
  }

  public DestinationDefinitionSpecificationRead getDestinationSpecification(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    UUID destinationId = destinationDefinitionIdRequestBody.getDestinationDefinitionId();
    StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationId);
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());
    final ConnectorSpecification spec = getConnectorSpecification(imageName);

    TrackingClientSingleton.get().track("get_destination_spec", ImmutableMap.<String, Object>builder()
        .put("image_name", imageName)
        .put("destination_name", destination.getName())
        .put("destination_id", destination.getDestinationDefinitionId())
        .build());

    return new DestinationDefinitionSpecificationRead()
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .destinationDefinitionId(destinationId);
  }

  public ConnectionSyncRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final SourceConnection sourceConnection =
        configRepository.getSourceConnection(standardSync.getSourceId());
    final DestinationConnection destinationConnection =
        configRepository.getDestinationConnection(standardSync.getDestinationId());

    StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
    final String sourceImageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());

    StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    final long jobId = schedulerPersistence.createSyncJob(
        sourceConnection,
        destinationConnection,
        standardSync,
        sourceImageName,
        destinationImageName);
    final Job job = waitUntilJobIsTerminalOrTimeout(jobId);

    TrackingClientSingleton.get().track("sync", ImmutableMap.<String, Object>builder()
        .put("name", standardSync.getName())
        .put("connection_id", standardSync.getConnectionId())
        .put("sync_mode", standardSync.getSyncMode())
        .put("source_id", sourceConnection.getSourceDefinitionId())
        .put("source_implementation_id", sourceConnection.getSourceId())
        .put("destination_implementation_id", destinationConnection.getDestinationId())
        .put("destination_id", destinationConnection.getDestinationDefinitionId())
        .put("job_id", jobId)
        .build());

    return new ConnectionSyncRead()
        .status(job.getStatus().equals(JobStatus.COMPLETED) ? ConnectionSyncRead.StatusEnum.SUCCEEDED : ConnectionSyncRead.StatusEnum.FAILED);
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
        .orElse(new StandardCheckConnectionOutput().withStatus(StandardCheckConnectionOutput.Status.FAILED));

    return new CheckConnectionRead()
        .status(Enums.convertTo(output.getStatus(), CheckConnectionRead.StatusEnum.class))
        .message(output.getMessage());
  }

}
