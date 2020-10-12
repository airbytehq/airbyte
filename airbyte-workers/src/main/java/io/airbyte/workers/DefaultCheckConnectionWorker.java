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

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultCheckConnectionWorker implements CheckConnectionWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultCheckConnectionWorker.class);

  private final DiscoverCatalogWorker discoverCatalogWorker;

  public DefaultCheckConnectionWorker(DiscoverCatalogWorker discoverCatalogWorker) {
    this.discoverCatalogWorker = discoverCatalogWorker;
  }

  @Override
  public OutputAndStatus<StandardCheckConnectionOutput> run(StandardCheckConnectionInput input, Path jobRoot) {

    final StandardDiscoverCatalogInput discoverSchemaInput = new StandardDiscoverCatalogInput()
        .withConnectionConfiguration(input.getConnectionConfiguration());

    final OutputAndStatus<StandardDiscoverCatalogOutput> outputAndStatus = discoverCatalogWorker.run(discoverSchemaInput, jobRoot);

    final JobStatus jobStatus;
    final StandardCheckConnectionOutput output = new StandardCheckConnectionOutput();
    if (outputAndStatus.getStatus() == JobStatus.SUCCESSFUL && outputAndStatus.getOutput().isPresent()) {
      output.withStatus(StandardCheckConnectionOutput.Status.SUCCESS);
      jobStatus = JobStatus.SUCCESSFUL;
    } else {
      LOGGER.info("Connection check unsuccessful. Discovery output: {}", outputAndStatus);
      jobStatus = JobStatus.FAILED;
      output.withStatus(StandardCheckConnectionOutput.Status.FAILURE)
          // TODO add better error log parsing to specify the exact reason for failure as the message
          .withMessage("Failed to connect.");
    }

    return new OutputAndStatus<>(jobStatus, output);
  }

  @Override
  public void cancel() {
    discoverCatalogWorker.cancel();
  }

}
