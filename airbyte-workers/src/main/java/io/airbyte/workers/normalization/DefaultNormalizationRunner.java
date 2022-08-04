/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationRunner implements NormalizationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationRunner.class);
  private static final MdcScope.Builder CONTAINER_LOG_MDC_BUILDER = new Builder()
      .setLogPrefix("normalization")
      .setPrefixColor(Color.GREEN_BACKGROUND);

  private final WorkerConfigs workerConfigs;
  private final DestinationType destinationType;
  private final ProcessFactory processFactory;
  private final String normalizationImageName;
  private final NormalizationAirbyteStreamFactory streamFactory = new NormalizationAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER);
  private Map<Type, List<AirbyteMessage>> airbyteMessagesByType;

  private Process process = null;

  public enum DestinationType {
    BIGQUERY,
    MSSQL,
    MYSQL,
    ORACLE,
    POSTGRES,
    REDSHIFT,
    SNOWFLAKE,
    CLICKHOUSE
  }

  public DefaultNormalizationRunner(final WorkerConfigs workerConfigs,
                                    final DestinationType destinationType,
                                    final ProcessFactory processFactory,
                                    final String normalizationImageName) {
    this.workerConfigs = workerConfigs;
    this.destinationType = destinationType;
    this.processFactory = processFactory;
    this.normalizationImageName = normalizationImageName;
  }

  @Override
  public boolean configureDbt(final String jobId,
                              final int attempt,
                              final Path jobRoot,
                              final JsonNode config,
                              final ResourceRequirements resourceRequirements,
                              final OperatorDbt dbtConfig)
      throws Exception {
    final Map<String, String> files = ImmutableMap.of(
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(config));
    final String gitRepoUrl = dbtConfig.getGitRepoUrl();
    if (Strings.isNullOrEmpty(gitRepoUrl)) {
      throw new WorkerException("Git Repo Url is required");
    }
    final String gitRepoBranch = dbtConfig.getGitRepoBranch();
    if (Strings.isNullOrEmpty(gitRepoBranch)) {
      return runProcess(jobId, attempt, jobRoot, files, resourceRequirements, "configure-dbt",
          "--integration-type", destinationType.toString().toLowerCase(),
          "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
          "--git-repo", gitRepoUrl);
    } else {
      return runProcess(jobId, attempt, jobRoot, files, resourceRequirements, "configure-dbt",
          "--integration-type", destinationType.toString().toLowerCase(),
          "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
          "--git-repo", gitRepoUrl,
          "--git-branch", gitRepoBranch);
    }
  }

  @Override
  public boolean normalize(final String jobId,
                           final int attempt,
                           final Path jobRoot,
                           final JsonNode config,
                           final ConfiguredAirbyteCatalog catalog,
                           final ResourceRequirements resourceRequirements)
      throws Exception {
    final Map<String, String> files = ImmutableMap.of(
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(config),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    return runProcess(jobId, attempt, jobRoot, files, resourceRequirements, "run",
        "--integration-type", destinationType.toString().toLowerCase(),
        "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        "--catalog", WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME);
  }

  private boolean runProcess(final String jobId,
                             final int attempt,
                             final Path jobRoot,
                             final Map<String, String> files,
                             final ResourceRequirements resourceRequirements,
                             final String... args)
      throws Exception {
    try {
      LOGGER.info("Running with normalization version: {}", normalizationImageName);
      process = processFactory.create(
          AirbyteIntegrationLauncher.NORMALIZE_STEP,
          jobId,
          attempt,
          jobRoot,
          normalizationImageName,
          false, files,
          null,
          resourceRequirements,
          Map.of(AirbyteIntegrationLauncher.JOB_TYPE, AirbyteIntegrationLauncher.SYNC_JOB, AirbyteIntegrationLauncher.SYNC_STEP,
              AirbyteIntegrationLauncher.NORMALIZE_STEP),
          Collections.emptyMap(),
          Collections.emptyMap(),
          args);

      try (final InputStream stdout = process.getInputStream()) {
        // finds and collects any AirbyteMessages from stdout
        // also builds a list of raw dbt errors and stores in streamFactory
        airbyteMessagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
            .collect(Collectors.groupingBy(AirbyteMessage::getType));

        // picks up error logs from dbt
        String dbtErrorStack = String.join("\n\t", streamFactory.getDbtErrors());

        if (!"".equals(dbtErrorStack)) {
          AirbyteMessage dbtTraceMessage = new AirbyteMessage()
              .withType(Type.TRACE)
              .withTrace(new AirbyteTraceMessage()
                  .withType(AirbyteTraceMessage.Type.ERROR)
                  .withEmittedAt((double) System.currentTimeMillis())
                  .withError(new AirbyteErrorTraceMessage()
                      .withFailureType(FailureType.SYSTEM_ERROR) // TODO: decide on best FailureType for this
                      .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                      .withInternalMessage(dbtErrorStack)
                      .withStackTrace(dbtErrorStack)));

          airbyteMessagesByType.putIfAbsent(Type.TRACE, List.of(dbtTraceMessage));
        }
      }
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error, CONTAINER_LOG_MDC_BUILDER);

      WorkerUtils.wait(process);

      return process.exitValue() == 0;
    } catch (final Exception e) {
      // make sure we kill the process on failure to avoid zombies.
      if (process != null) {
        WorkerUtils.cancelProcess(process);
      }
      throw e;
    }
  }

  @Override
  public void close() throws Exception {
    if (process == null) {
      return;
    }

    LOGGER.debug("Closing normalization process");
    WorkerUtils.gentleClose(workerConfigs, process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      throw new WorkerException("Normalization process wasn't successful");
    }
  }

  @Override
  public Stream<AirbyteTraceMessage> getTraceMessages() {
    if (airbyteMessagesByType != null && airbyteMessagesByType.get(Type.TRACE) != null) {
      return airbyteMessagesByType.get(Type.TRACE).stream().map(AirbyteMessage::getTrace);
    }
    return Stream.empty();
  }

  @VisibleForTesting
  DestinationType getDestinationType() {
    return destinationType;
  }

}
