/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationRunner implements NormalizationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationRunner.class);
  private static final MdcScope.Builder CONTAINER_LOG_MDC_BUILDER = new Builder()
      .setLogPrefix("normalization")
      .setPrefixColor(Color.GREEN);

  private final DestinationType destinationType;
  private final ProcessFactory processFactory;
  private final String normalizationImageName;

  private Process process = null;

  public enum DestinationType {
    BIGQUERY,
    MSSQL,
    MYSQL,
    ORACLE,
    POSTGRES,
    REDSHIFT,
    SNOWFLAKE
  }

  public DefaultNormalizationRunner(final DestinationType destinationType, final ProcessFactory processFactory, final String normalizationImageName) {
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
      process = processFactory.create(jobId, attempt, jobRoot, normalizationImageName, false, files, null, resourceRequirements,
          Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.NORMALISE_STEP), args);

      LineGobbler.gobble(process.getInputStream(), LOGGER::info, CONTAINER_LOG_MDC_BUILDER);
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
    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      throw new WorkerException("Normalization process wasn't successful");
    }
  }

  @VisibleForTesting
  DestinationType getDestinationType() {
    return destinationType;
  }

}
