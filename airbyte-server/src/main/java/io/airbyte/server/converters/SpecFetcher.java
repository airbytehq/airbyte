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

package io.airbyte.server.converters;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.DefaultSchedulerSynchronousJobClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SchedulerSynchronousJobClient;
import io.airbyte.scheduler.client.SynchronousJobException;
import java.io.IOException;

public class SpecFetcher {

  private final SchedulerSynchronousJobClient schedulerJobClient;

  public SpecFetcher(SchedulerSynchronousJobClient schedulerJobClient) {
    this.schedulerJobClient = schedulerJobClient;
  }

  public SpecFetcher(SchedulerJobClient schedulerJobClient) {
    this(new DefaultSchedulerSynchronousJobClient(schedulerJobClient));
  }

  public ConnectorSpecification execute(String dockerImage) throws IOException {
    try {
      return schedulerJobClient.createGetSpecJob(dockerImage).getSpecification();
    } catch (IOException | SynchronousJobException e) {
      throw new RuntimeException("failed to fetch spec.", e);
    }
  }

}
