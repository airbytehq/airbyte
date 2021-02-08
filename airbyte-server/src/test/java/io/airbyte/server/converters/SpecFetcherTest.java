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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.client.SchedulerJobClient;
import java.io.IOException;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SpecFetcherTest {

  private static final String IMAGE_NAME = "foo:bar";

  private SchedulerJobClient schedulerJobClient;
  private Job job;
  private JobOutput jobOutput;
  private ConnectorSpecification connectorSpecification;
  private StandardGetSpecOutput specOutput;

  @BeforeEach
  void setup() {
    schedulerJobClient = mock(SchedulerJobClient.class);
    job = mock(Job.class);
    jobOutput = mock(JobOutput.class);
    connectorSpecification = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));
    specOutput = new StandardGetSpecOutput().withSpecification(connectorSpecification);

    when(job.getSuccessOutput()).thenReturn(Optional.ofNullable(jobOutput));

  }

  @Test
  void testFetch() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(job);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.execute(IMAGE_NAME));
  }

  @Test
  void testFetchEmpty() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(job);
    when(job.getSuccessOutput()).thenReturn(Optional.empty());

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertThrows(IllegalArgumentException.class, () -> specFetcher.execute(IMAGE_NAME));
  }

}
