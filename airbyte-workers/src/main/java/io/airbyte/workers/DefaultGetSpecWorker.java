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

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultGetSpecWorker implements GetSpecWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecWorker.class);

  private final IntegrationLauncher integrationLauncher;

  private Process process;

  public DefaultGetSpecWorker(final IntegrationLauncher integrationLauncher) {
    this.integrationLauncher = integrationLauncher;
  }

  @Override
  public OutputAndStatus<StandardGetSpecOutput> run(JobGetSpecConfig config, Path jobRoot) {
    try {
      process = integrationLauncher.spec(jobRoot).start();
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      try (InputStream stdout = process.getInputStream()) {
        // retrieving spec should generally be instantaneous
        WorkerUtils.gentleClose(process, 10, TimeUnit.SECONDS);

        if (process.exitValue() == 0) {
          String specString = new String(stdout.readAllBytes());
          ConnectorSpecification spec = Jsons.deserialize(specString, ConnectorSpecification.class);
          return new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardGetSpecOutput().withSpecification(spec));
        } else {
          return new OutputAndStatus<>(JobStatus.FAILED);
        }
      }

    } catch (Exception e) {
      LOGGER.error("Error while getting spec from image {}: {}", config.getDockerImage(), e);
      return new OutputAndStatus<>(JobStatus.FAILED);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
