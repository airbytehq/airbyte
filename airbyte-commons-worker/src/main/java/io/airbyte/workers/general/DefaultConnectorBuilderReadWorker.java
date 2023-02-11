/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTOR_VERSION_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.SOURCE_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;
import static io.airbyte.workers.process.Metadata.CONNECTOR_JOB;
import static io.airbyte.workers.process.Metadata.DISCOVER_JOB;
import static io.airbyte.workers.process.Metadata.JOB_TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.model.generated.DiscoverCatalogResult;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaWriteRequestBody;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.Configs;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.FailureReason;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.WorkerEnvConstants;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteControlConnectorConfigMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.CatalogClientConverters;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultConnectorBuilderReadWorker implements ConnectorBuilderReadWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultConnectorBuilderReadWorker.class);
  private static final String WRITE_DISCOVER_CATALOG_LOGS_TAG = "call to write discover schema result";

  private final AirbyteStreamFactory streamFactory;
  private final ConnectorConfigUpdater connectorConfigUpdater;
  private String jobId;
  private String imageName;
  private final AirbyteApiClient airbyteApiClient;
  private final ProcessFactory processFactory;

  private volatile Process process;

  public DefaultConnectorBuilderReadWorker(final AirbyteApiClient airbyteApiClient,
                                           final ProcessFactory processFactory,
                                           final ConnectorConfigUpdater connectorConfigUpdater,
                                           final AirbyteStreamFactory streamFactory,
                                           final String jobId,
                                           final String imageName) {
    this.airbyteApiClient = airbyteApiClient;
    this.processFactory = processFactory;
    this.streamFactory = streamFactory;
    this.connectorConfigUpdater = connectorConfigUpdater;
    this.jobId = jobId;
    this.imageName = imageName;
  }

  public DefaultConnectorBuilderReadWorker(final AirbyteApiClient airbyteApiClient,
                                           final ProcessFactory processFactory,
                                           final ConnectorConfigUpdater connectorConfigUpdater,
                                           final String jobId,
                                           final String imageName) {
    this(airbyteApiClient, processFactory, connectorConfigUpdater, new DefaultAirbyteStreamFactory(), jobId, imageName);
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public ConnectorJobOutput run(final StandardConnectorBuilderReadInput connectorBuilderReadInput, final Path jobRoot) throws WorkerException {
    ApmTraceUtils.addTagsToTrace(generateTraceTags(connectorBuilderReadInput, jobRoot));
    try {
      ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, jobId, JOB_ROOT_KEY, jobRoot, DOCKER_IMAGE_KEY, "image_name_from_worker")); //FIXME
      process = processFactory.create(
          CONNECTOR_JOB,
          jobId,
          0, //FIXME Pass as parameter
          jobRoot,
          imageName,
          false,
          false,
          ImmutableMap.of(),
          null,
          new ResourceRequirements(),
          new AllowedHosts(),
          Map.of(JOB_TYPE_KEY, DISCOVER_JOB),
          getWorkerMetadata(),
          Collections.emptyMap());

      final ConnectorJobOutput jobOutput = new ConnectorJobOutput()
          .withOutputType(OutputType.CONNECTOR_BUILDER_READ);

      return jobOutput;
    } catch (final WorkerException e) {
      ApmTraceUtils.addExceptionToTrace(e);
      throw e;
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      throw new WorkerException("Error while discovering schema", e);
    }
  }

  private SourceDiscoverSchemaWriteRequestBody buildSourceDiscoverSchemaWriteRequestBody(final StandardDiscoverCatalogInput discoverSchemaInput,
                                                                                         final AirbyteCatalog catalog) {
    return new SourceDiscoverSchemaWriteRequestBody().catalog(
        CatalogClientConverters.toAirbyteCatalogClientApi(catalog)).sourceId(
            // NOTE: sourceId is marked required in the OpenAPI config but the code generator doesn't enforce
            // it, so we check again here.
            discoverSchemaInput.getSourceId() == null ? null : UUID.fromString(discoverSchemaInput.getSourceId()))
        .connectorVersion(
            discoverSchemaInput.getConnectorVersion())
        .configurationHash(
            discoverSchemaInput.getConfigHash());
  }

  private Map<String, Object> generateTraceTags(final StandardConnectorBuilderReadInput connectorBuilderReadInput, final Path jobRoot) {
    final Map<String, Object> tags = new HashMap<>();
    //FIXME this whole method
    tags.put(JOB_ROOT_KEY, jobRoot);

    return tags;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

  private Map<String, String> getWorkerMetadata() {
    final Configs configs = new EnvConfigs();
    // We've managed to exceed the maximum number of parameters for Map.of(), so use a builder + convert
    // back to hashmap
    return Maps.newHashMap(
        ImmutableMap.<String, String>builder()
            .put(WorkerEnvConstants.WORKER_CONNECTOR_IMAGE, imageName)
            .put(WorkerEnvConstants.WORKER_JOB_ID, jobId)
            //.put(WorkerEnvConstants.WORKER_JOB_ATTEMPT, String.valueOf(attempt))
            //.put(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, String.valueOf(featureFlags.useStreamCapableState()))
            //.put(EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA, String.valueOf(featureFlags.autoDetectSchema()))
            //.put(EnvVariableFeatureFlags.APPLY_FIELD_SELECTION, String.valueOf(featureFlags.applyFieldSelection()))
            //.put(EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES, featureFlags.fieldSelectionWorkspaces())
            //.put(EnvVariableFeatureFlags.STRICT_COMPARISON_NORMALIZATION_WORKSPACES, featureFlags.strictComparisonNormalizationWorkspaces())
            //.put(EnvVariableFeatureFlags.STRICT_COMPARISON_NORMALIZATION_TAG, featureFlags.strictComparisonNormalizationTag())
            .put(EnvConfigs.SOCAT_KUBE_CPU_LIMIT, configs.getSocatSidecarKubeCpuLimit())
            .put(EnvConfigs.SOCAT_KUBE_CPU_REQUEST, configs.getSocatSidecarKubeCpuRequest())
            .put(EnvConfigs.LAUNCHDARKLY_KEY, configs.getLaunchDarklyKey())
            .put(EnvConfigs.FEATURE_FLAG_CLIENT, configs.getFeatureFlagClient())
            .build());
  }

}
