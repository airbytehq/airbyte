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
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.OperatorDbt;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.apache.tools.ant.types.Commandline;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DbtTransformationRunner implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationRunner.class);

  private final ProcessBuilderFactory pbf;
  private final NormalizationRunner normalizationRunner;
  private Process process = null;

  public DbtTransformationRunner(final ProcessBuilderFactory pbf, NormalizationRunner normalizationRunner) {
    this.pbf = pbf;
    this.normalizationRunner = normalizationRunner;
  }

  public void start() throws Exception {
    normalizationRunner.start();
  }

  /**
   * Re-use the Normalization runner to configure the dbt project with the correct destination settings and then
   * run the custom transformation command.
   */
  public boolean run(String jobId, int attempt, Path jobRoot, JsonNode config, OperatorDbt dbtConfig) throws Exception {
    if (!normalizationRunner.configureDbt(jobId, attempt, jobRoot, config, dbtConfig)) {
      return false;
    }
    return transform(jobId, attempt, jobRoot, config, dbtConfig);
  }

  public boolean transform(String jobId, int attempt, Path jobRoot, JsonNode config, OperatorDbt dbtConfig) throws Exception {
    IOs.writeFile(jobRoot, WorkerConstants.CUSTOM_ENTRYPOINT_SH, MoreResources.readResource("dbt_transformation_entrypoint.sh"));
    try {
      final List<String> dbtArguments = new ArrayList<>();
      dbtArguments.add("/data/job/transform/" + WorkerConstants.CUSTOM_ENTRYPOINT_SH);
      Collections.addAll(dbtArguments, Commandline.translateCommandline(dbtConfig.getDbtArguments()));
      if (!dbtConfig.getDbtArguments().contains("--profiles-dir=")) {
        dbtArguments.add("--profiles-dir=/data/job/transform/");
      }
      if (!dbtConfig.getDbtArguments().contains("--project-dir=")) {
        dbtArguments.add("--project-dir=/data/job/transform/git_repo/");
      }
      process = pbf.create(jobId, attempt, jobRoot, dbtConfig.getDockerImage(), "/bin/bash", dbtArguments).start();

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
