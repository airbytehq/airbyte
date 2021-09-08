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

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.ResourceRequirements;
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

  private final ProcessFactory processFactory;
  private final NormalizationRunner normalizationRunner;
  private Process process = null;

  public DbtTransformationRunner(final ProcessFactory processFactory, NormalizationRunner normalizationRunner) {
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
   *
   * Once the workspace folder/files is setup to run, we invoke the custom transformation command as
   * provided by the user to execute whatever extra transformation has been implemented.
   */
  public boolean run(String jobId, int attempt, Path jobRoot, JsonNode config, ResourceRequirements resourceRequirements, OperatorDbt dbtConfig)
      throws Exception {
    if (!normalizationRunner.configureDbt(jobId, attempt, jobRoot, config, resourceRequirements, dbtConfig)) {
      return false;
    }
    return transform(jobId, attempt, jobRoot, config, resourceRequirements, dbtConfig);
  }

  public boolean transform(String jobId, int attempt, Path jobRoot, JsonNode config, ResourceRequirements resourceRequirements, OperatorDbt dbtConfig)
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
          processFactory.create(jobId, attempt, jobRoot, dbtConfig.getDockerImage(), false, files, "/bin/bash", resourceRequirements, dbtArguments);

      LineGobbler.gobble(process.getInputStream(), LOGGER::info);
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      WorkerUtils.wait(process);

      return process.exitValue() == 0;
    } catch (Exception e) {
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
