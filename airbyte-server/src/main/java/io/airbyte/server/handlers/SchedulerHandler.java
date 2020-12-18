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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.SourceCoreConfig;
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
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.SchemaConverter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;

public class SchedulerHandler {

  private final ConfigRepository configRepository;
  private final SchedulerJobClient schedulerJobClient;
  private final Supplier<UUID> uuidSupplier;

  @VisibleForTesting
  SchedulerHandler(final ConfigRepository configRepository, SchedulerJobClient schedulerJobClient, Supplier<UUID> uuidSupplier) {
    this.configRepository = configRepository;
    this.schedulerJobClient = schedulerJobClient;
    this.uuidSupplier = uuidSupplier;
  }

  public SchedulerHandler(final ConfigRepository configRepository, SchedulerJobClient schedulerJobClient) {
    this(configRepository, schedulerJobClient, UUID::randomUUID);
  }

  public CheckConnectionRead checkSourceConnectionFromSourceId(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    return reportConnectionStatus(schedulerJobClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkSourceConnectionFromSourceCreate(SourceCoreConfig sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceCreate.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    final UUID sourceUuid = uuidSupplier.get();
    final SourceConnection source = new SourceConnection()
        .withName("source:" + sourceUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withSourceDefinitionId(sourceCreate.getSourceDefinitionId())
        .withWorkspaceId(sourceUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withTombstone(false)
        // todo (cgardens) - used to create the scope so we want a random value.
        .withSourceId(sourceUuid)
        .withConfiguration(sourceCreate.getConnectionConfiguration());

    return reportConnectionStatus(schedulerJobClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationId(DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationConnection destination = configRepository.getDestinationConnection(destinationIdRequestBody.getDestinationId());
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());
    return reportConnectionStatus(schedulerJobClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationCreate(DestinationCoreConfig destinationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition destDef = configRepository.getStandardDestinationDefinition(destinationCreate.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destDef.getDockerRepository(), destDef.getDockerImageTag());
    final UUID destinationUuid = uuidSupplier.get();
    final DestinationConnection destination = new DestinationConnection()
        .withName("destination:" + destinationUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withDestinationDefinitionId(destinationCreate.getDestinationDefinitionId())
        .withWorkspaceId(destinationUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withTombstone(false)
        // todo (cgardens) - used to create the scope so we want a random value.
        .withDestinationId(destinationUuid)
        .withConfiguration(destinationCreate.getConnectionConfiguration());
    return reportConnectionStatus(schedulerJobClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceId(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    final Job job = schedulerJobClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(job);
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceCreate(SourceCoreConfig sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceCreate.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    final UUID sourceUuid = uuidSupplier.get();
    final SourceConnection source = new SourceConnection()
        .withName("source:" + sourceUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withSourceDefinitionId(sourceCreate.getSourceDefinitionId())
        .withWorkspaceId(sourceUuid) // todo (cgardens) - narrow the struct passed to the client.
        .withTombstone(false)
        // todo (cgardens) - used to create the scope so we want a random value.
        .withSourceId(sourceUuid)
        .withConfiguration(sourceCreate.getConnectionConfiguration());
    final Job job = schedulerJobClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(job);
  }

  private static SourceDiscoverSchemaRead discoverJobToOutput(Job job) {
    StandardDiscoverCatalogOutput discoverOutput = job.getSuccessOutput()
        .map(JobOutput::getDiscoverCatalog)
        .orElseThrow(() -> new IllegalStateException("no discover output found"));
    final Schema schema = AirbyteProtocolConverters.toSchema(discoverOutput.getCatalog());

    return new SourceDiscoverSchemaRead()
        .schema(SchemaConverter.toApiSchema(schema))
        .jobInfo(JobConverter.getJobInfoRead(job));
  }

  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID sourceDefinitionId = sourceDefinitionIdRequestBody.getSourceDefinitionId();
    final StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final String imageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
    final ConnectorSpecification spec = getConnectorSpecification(imageName);
    return new SourceDefinitionSpecificationRead()
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .sourceDefinitionId(sourceDefinitionId);
  }

  public DestinationDefinitionSpecificationRead getDestinationSpecification(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID destinationDefinitionId = destinationDefinitionIdRequestBody.getDestinationDefinitionId();
    final StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());
    final ConnectorSpecification spec = getConnectorSpecification(imageName);
    return new DestinationDefinitionSpecificationRead()
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .destinationDefinitionId(destinationDefinitionId);
  }

  public ConnectorSpecification getConnectorSpecification(String dockerImage) throws IOException {
    return schedulerJobClient.createGetSpecJob(dockerImage)
        .getSuccessOutput()
        .map(JobOutput::getGetSpec)
        .map(StandardGetSpecOutput::getSpecification)
        .orElseThrow(() -> new IllegalStateException("no spec output found"));
  }

  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final SourceConnection source = configRepository.getSourceConnection(standardSync.getSourceId());
    final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String sourceImageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final Job job = schedulerJobClient.createSyncJob(
        source,
        destination,
        standardSync,
        sourceImageName,
        destinationImageName);

    return JobConverter.getJobInfoRead(job);
  }

  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final Job job = schedulerJobClient.createResetConnectionJob(destination, standardSync, destinationImageName);

    return JobConverter.getJobInfoRead(job);
  }

  private CheckConnectionRead reportConnectionStatus(final Job job) {
    final StandardCheckConnectionOutput checkConnectionOutput = job.getSuccessOutput().map(JobOutput::getCheckConnection)
        // the job should always produce an output, but if it does not, we assume a failure.
        .orElse(new StandardCheckConnectionOutput().withStatus(Status.FAILED));

    return new CheckConnectionRead()
        .status(Enums.convertTo(checkConnectionOutput.getStatus(), CheckConnectionRead.StatusEnum.class))
        .message(checkConnectionOutput.getMessage())
        .jobInfo(JobConverter.getJobInfoRead(job));
  }

}
