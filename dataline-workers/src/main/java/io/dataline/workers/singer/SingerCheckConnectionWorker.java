/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.singer;

import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerCheckConnectionWorker
    extends BaseSingerWorker<StandardCheckConnectionInput, StandardCheckConnectionOutput>
    implements CheckConnectionWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerCheckConnectionWorker.class);

  private final SingerDiscoverSchemaWorker singerDiscoverSchemaWorker;

  public SingerCheckConnectionWorker(SingerConnector connector) {
    super(connector);
    this.singerDiscoverSchemaWorker = new SingerDiscoverSchemaWorker(connector);
  }

  @Override
  OutputAndStatus<StandardCheckConnectionOutput> runInternal(
      StandardCheckConnectionInput input, Path workspaceRoot) {

    final StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput();
    discoverSchemaInput.setConnectionConfiguration(input.getConnectionConfiguration());

    OutputAndStatus<StandardDiscoverSchemaOutput> outputAndStatus =
        singerDiscoverSchemaWorker.runInternal(discoverSchemaInput, workspaceRoot);
    StandardCheckConnectionOutput output = new StandardCheckConnectionOutput();
    JobStatus jobStatus;
    if (outputAndStatus.getStatus() == JobStatus.SUCCESSFUL
        && outputAndStatus.getOutput().isPresent()) {
      output.setStatus(StandardCheckConnectionOutput.Status.SUCCESS);
      jobStatus = JobStatus.SUCCESSFUL;
    } else {
      LOGGER.info("Connection check unsuccessful. Discovery output: {}", outputAndStatus);
      jobStatus = JobStatus.FAILED;
      output.setStatus(StandardCheckConnectionOutput.Status.FAILURE);
      // TODO add better error log parsing to specify the exact reason for failure as the message
      output.setMessage("Failed to connect.");
    }

    return new OutputAndStatus<>(jobStatus, output);
  }

  @Override
  public void cancel() {
    singerDiscoverSchemaWorker.cancel();
  }
}
