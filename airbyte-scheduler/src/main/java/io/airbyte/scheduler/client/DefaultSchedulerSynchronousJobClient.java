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

package io.airbyte.scheduler.client;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobOutput;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.scheduler.Job;
import java.io.IOException;

public class DefaultSchedulerSynchronousJobClient implements SchedulerSynchronousJobClient {

  private final SchedulerJobClient schedulerJobClient;

  public DefaultSchedulerSynchronousJobClient(SchedulerJobClient schedulerJobClient) {
    this.schedulerJobClient = schedulerJobClient;
  }

  @Override
  public StandardCheckConnectionOutput createSourceCheckConnectionJob(SourceConnection source, String dockerImage)
      throws IOException, SynchronousJobException {
    return unwrapCheckConnectionJob(schedulerJobClient.createSourceCheckConnectionJob(source, dockerImage));
  }

  @Override
  public StandardCheckConnectionOutput createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImage)
      throws IOException, SynchronousJobException {
    return unwrapCheckConnectionJob(schedulerJobClient.createDestinationCheckConnectionJob(destination, dockerImage));
  }

  private static StandardCheckConnectionOutput unwrapCheckConnectionJob(Job job) throws SynchronousJobException {
    return job.getSuccessOutput().map(JobOutput::getCheckConnection).orElseThrow(() -> getExceptionFromJob(job));
  }

  @Override
  public StandardDiscoverCatalogOutput createDiscoverSchemaJob(SourceConnection source, String dockerImage)
      throws IOException, SynchronousJobException {
    final Job job = schedulerJobClient.createDiscoverSchemaJob(source, dockerImage);
    return job.getSuccessOutput().map(JobOutput::getDiscoverCatalog).orElseThrow(() -> getExceptionFromJob(job));
  }

  @Override
  public StandardGetSpecOutput createGetSpecJob(String dockerImage) throws IOException, SynchronousJobException {
    final Job job = schedulerJobClient.createGetSpecJob(dockerImage);
    return job.getSuccessOutput().map(JobOutput::getGetSpec).orElseThrow(() -> getExceptionFromJob(job));
  }

  private static SynchronousJobException getExceptionFromJob(Job job) {
    return new SynchronousJobException(JobMetadatas.fromJob(job));
  }

}
