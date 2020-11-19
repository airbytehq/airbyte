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

package io.airbyte.integrations.base.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationRunner implements NormalizationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationRunner.class);

  public static final String CONFIG_JSON_FILENAME = "destination_config.json";
  public static final String CATALOG_JSON_FILENAME = "json_catalog.json";

  private final DestinationType destinationType;

  private Process process = null;

  public enum DestinationType {
    BIGQUERY,
    POSTGRES,
    SNOWFLAKE
  }

  public DefaultNormalizationRunner(final DestinationType destinationType) {
    this.destinationType = destinationType;
  }

  @Override
  public boolean normalize(Path jobRoot, JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(config));
    IOs.writeFile(jobRoot, CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    try {
      process = createProcess(jobRoot, "run",
          "--integration-type", destinationType.toString().toLowerCase(),
          "--config", CONFIG_JSON_FILENAME,
          "--catalog", CATALOG_JSON_FILENAME).start();
      LineGobbler.gobble(process.getInputStream(), LOGGER::info);
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);
      try {
        process.waitFor();
      } catch (InterruptedException e) {
        LOGGER.error("Exception while while waiting for process to finish", e);
      }
      return process.exitValue() == 0;
    } catch (Exception e) {
      // make sure we kill the process on failure to avoid zombies.
      if (process != null) {
        try {
          process.destroy();
          process.waitFor(1, TimeUnit.MINUTES);
          if (process.isAlive()) {
            process.destroyForcibly();
          }
        } catch (InterruptedException ei) {
          LOGGER.error("Exception when closing process.", ei);
        }
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
    try {
      process.waitFor(1, TimeUnit.MINUTES);
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }

    if (process.isAlive() || process.exitValue() != 0) {
      throw new Exception("Normalization process wasn't successful");
    }
  }

  @VisibleForTesting
  DestinationType getDestinationType() {
    return destinationType;
  }

  private ProcessBuilder createProcess(Path jobRoot, final String... args) {
    final List<String> cmd =
        Lists.newArrayList("bash", "/airbyte/normalize.sh");
    cmd.addAll(Arrays.asList(args));
    LOGGER.debug("Preparing command: {}", Joiner.on(" ").join(cmd));
    return new ProcessBuilder(cmd).directory(jobRoot.toFile());
  }

}
