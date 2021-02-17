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

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationRunner implements NormalizationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationRunner.class);

  public static final String NORMALIZATION_IMAGE_NAME = "airbyte/normalization:0.1.12";

  private final DestinationType destinationType;
  private final ProcessBuilderFactory pbf;

  private Process process = null;

  public enum DestinationType {
    BIGQUERY,
    POSTGRES,
    REDSHIFT,
    SNOWFLAKE
  }

  public DefaultNormalizationRunner(final DestinationType destinationType, final ProcessBuilderFactory pbf) {
    this.destinationType = destinationType;
    this.pbf = pbf;
  }

  @Override
  public boolean normalize(long jobId, int attempt, Path jobRoot, JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    IOs.writeFile(jobRoot, WorkerConstants.TARGET_CONFIG_JSON_FILENAME, Jsons.serialize(config));
    IOs.writeFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    try {
      process = pbf.create(jobId, attempt, jobRoot, NORMALIZATION_IMAGE_NAME, "run",
          "--integration-type", destinationType.toString().toLowerCase(),
          "--config", WorkerConstants.TARGET_CONFIG_JSON_FILENAME,
          "--catalog", WorkerConstants.CATALOG_JSON_FILENAME).start();

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
    if (process == null) {
      return;
    }

    LOGGER.debug("Closing tap process");
    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      throw new WorkerException("Tap process wasn't successful");
    }
  }

  @VisibleForTesting
  DestinationType getDestinationType() {
    return destinationType;
  }

}
