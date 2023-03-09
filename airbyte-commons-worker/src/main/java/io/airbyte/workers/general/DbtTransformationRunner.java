/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.workers.process.Metadata.CUSTOM_STEP;
import static io.airbyte.workers.process.Metadata.JOB_TYPE_KEY;
import static io.airbyte.workers.process.Metadata.SYNC_JOB;
import static io.airbyte.workers.process.Metadata.SYNC_STEP_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.apache.tools.ant.types.Commandline;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DbtTransformationRunner implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationRunner.class);
  private static final String DBT_ENTRYPOINT_SH = "entrypoint.sh";
  private static final MdcScope.Builder CONTAINER_LOG_MDC_BUILDER = new Builder()
      .setLogPrefix("dbt")
      .setPrefixColor(Color.PURPLE_BACKGROUND);

  private final ProcessFactory processFactory;
  private final NormalizationRunner normalizationRunner;
  private Process process = null;

  public DbtTransformationRunner(final ProcessFactory processFactory,
                                 final NormalizationRunner normalizationRunner) {
    this.processFactory = processFactory;
    this.normalizationRunner = normalizationRunner;
  }

  public void start() throws Exception {
    normalizationRunner.start();
  }

  /**
   * The docker image used by the DbtTransformationRunner is provided by the User, so we can't ensure
   * to have the right python, dbt, dependencies etc software installed to successfully run our
   * transform-config scripts (to translate Airbyte Catalogs into Dbt profiles file). Thus, we depend
   * on the NormalizationRunner to configure the dbt project with the appropriate destination settings
   * and pull the custom git repository into the workspace.
   * <p>
   * Once the workspace folder/files is setup to run, we invoke the custom transformation command as
   * provided by the user to execute whatever extra transformation has been implemented.
   */
  public boolean run(final String jobId,
                     final int attempt,
                     final Path jobRoot,
                     final JsonNode config,
                     final ResourceRequirements resourceRequirements,
                     final OperatorDbt dbtConfig)
      throws Exception {
    if (!normalizationRunner.configureDbt(jobId, attempt, jobRoot, config, resourceRequirements, dbtConfig)) {
      return false;
    }
    return transform(jobId, attempt, jobRoot, config, resourceRequirements, dbtConfig);
  }

  public boolean transform(final String jobId,
                           final int attempt,
                           final Path jobRoot,
                           final JsonNode config,
                           final ResourceRequirements resourceRequirements,
                           final OperatorDbt dbtConfig)
      throws Exception {
    try {
      final Map<String, String> files = ImmutableMap.of(
          DBT_ENTRYPOINT_SH, MoreResources.readResource("dbt_transformation_entrypoint.sh"),
          "sshtunneling.sh", MoreResources.readResource("sshtunneling.sh"));
      final List<String> dbtArguments = new ArrayList<>();
      dbtArguments.add(DBT_ENTRYPOINT_SH);
      if (Strings.isNullOrEmpty(dbtConfig.getDbtArguments())) {
        throw new WorkerException("Dbt Arguments are required");
      }
      Collections.addAll(dbtArguments, Commandline.translateCommandline(dbtConfig.getDbtArguments()));
      process =
          processFactory.create(
              CUSTOM_STEP,
              jobId,
              attempt,
              jobRoot,
              dbtConfig.getDockerImage(),
              false,
              false,
              files,
              "/bin/bash",
              resourceRequirements,
              null,
              Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, CUSTOM_STEP),
              Collections.emptyMap(),
              Collections.emptyMap(),
              dbtArguments.toArray(new String[0]));
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
    normalizationRunner.close();

    if (process == null) {
      return;
    }

    LOGGER.debug("Closing dbt transformation process");
    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      throw new WorkerException("Dbt transformation process wasn't successful");
    }
  }

}
