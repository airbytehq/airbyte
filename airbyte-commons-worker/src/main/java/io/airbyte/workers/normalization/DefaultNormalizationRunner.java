/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import static io.airbyte.workers.process.Metadata.JOB_TYPE_KEY;
import static io.airbyte.workers.process.Metadata.NORMALIZE_STEP;
import static io.airbyte.workers.process.Metadata.SYNC_JOB;
import static io.airbyte.workers.process.Metadata.SYNC_STEP_KEY;

import com.fasterxml.jackson.databind.JsonNode;
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
import io.airbyte.persistence.job.errorreporter.SentryExceptionHelper;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
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

  private final String normalizationIntegrationType;
  private final ProcessFactory processFactory;
  private final String normalizationImageName;
  private final NormalizationAirbyteStreamFactory streamFactory = new NormalizationAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER);
  private Map<Type, List<AirbyteMessage>> airbyteMessagesByType;
  private String dbtErrorStack;

  private Process process = null;

  public DefaultNormalizationRunner(final ProcessFactory processFactory,
                                    final String normalizationImage,
                                    final String normalizationIntegrationType) {
    this.processFactory = processFactory;
    this.normalizationImageName = normalizationImage;
    this.normalizationIntegrationType = normalizationIntegrationType;
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
          "--integration-type", normalizationIntegrationType.toLowerCase(),
          "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
          "--git-repo", gitRepoUrl);
    } else {
      return runProcess(jobId, attempt, jobRoot, files, resourceRequirements, "configure-dbt",
          "--integration-type", normalizationIntegrationType.toLowerCase(),
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
        "--integration-type", normalizationIntegrationType.toLowerCase(),
        "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        "--catalog", WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME);
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
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
          NORMALIZE_STEP,
          jobId,
          attempt,
          jobRoot,
          normalizationImageName,
          // custom connector does not use normalization
          false,
          false, files,
          null,
          resourceRequirements,
          null,
          Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, NORMALIZE_STEP),
          Collections.emptyMap(),
          Collections.emptyMap(),
          args);

      try (final InputStream stdout = process.getInputStream()) {
        // finds and collects any AirbyteMessages from stdout
        // also builds a list of raw dbt errors and stores in streamFactory
        airbyteMessagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
            .collect(Collectors.groupingBy(AirbyteMessage::getType));

        // picks up error logs from dbt
        dbtErrorStack = String.join("\n", streamFactory.getDbtErrors());

        if (!"".equals(dbtErrorStack)) {
          final AirbyteMessage dbtTraceMessage = new AirbyteMessage()
              .withType(Type.TRACE)
              .withTrace(new AirbyteTraceMessage()
                  .withType(AirbyteTraceMessage.Type.ERROR)
                  .withEmittedAt((double) System.currentTimeMillis())
                  .withError(new AirbyteErrorTraceMessage()
                      .withFailureType(FailureType.SYSTEM_ERROR) // TODO: decide on best FailureType for this
                      .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                      .withInternalMessage(buildInternalErrorMessageFromDbtStackTrace())
                      // due to the lack of consistent defining features in dbt errors we're injecting a breadcrumb to the
                      // stacktrace so we can confidently identify all dbt errors when parsing and sending to Sentry
                      // see dbt error examples: https://docs.getdbt.com/guides/legacy/debugging-errors for more context
                      .withStackTrace("AirbyteDbtError: \n".concat(dbtErrorStack))));

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

    LOGGER.info("Terminating normalization process...");
    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);

    /*
     * After attempting to close the process check the following:
     *
     * Did the process actually terminate? If "yes", did it do so nominally?
     */
    if (process.isAlive()) {
      throw new WorkerException("Normalization process did not terminate after 1 minute.");
    } else if (process.exitValue() != 0) {
      throw new WorkerException("Normalization process did not terminate normally (exit code: " + process.exitValue() + ")");
    } else {
      LOGGER.info("Normalization process successfully terminated.");
    }
  }

  @Override
  public Stream<AirbyteTraceMessage> getTraceMessages() {
    if (airbyteMessagesByType != null && airbyteMessagesByType.get(Type.TRACE) != null) {
      return airbyteMessagesByType.get(Type.TRACE).stream().map(AirbyteMessage::getTrace);
    }
    return Stream.empty();
  }

  private String buildInternalErrorMessageFromDbtStackTrace() {
    final Map<SentryExceptionHelper.ERROR_MAP_KEYS, String> errorMap = SentryExceptionHelper.getUsefulErrorMessageAndTypeFromDbtError(dbtErrorStack);
    return errorMap.get(SentryExceptionHelper.ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY);
  }

}
