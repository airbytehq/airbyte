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

package io.airbyte.server.validators;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.server.errors.KnownException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DockerImageValidatorTest {

  private SchedulerJobClient schedulerJobClient;
  private DockerImageValidator validator;

  @BeforeEach
  public void init() {
    schedulerJobClient = mock(SchedulerJobClient.class);
    validator = new DockerImageValidator(schedulerJobClient);
  }

  @Test
  public void testAssertImageIsValid() throws URISyntaxException, IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);

    final Job job = mock(Job.class);
    final ConnectorSpecification connectorSpecification = new ConnectorSpecification()
        .withDocumentationUrl(new URI("https://google.com"))
        .withChangelogUrl(new URI("https://google.com"))
        .withConnectionSpecification(Jsons.jsonNode(new HashMap<>()));
    when(schedulerJobClient.createGetSpecJob(imageName)).thenReturn(job);
    when(job.getSuccessOutput())
        .thenReturn(Optional.of(new JobOutput().withGetSpec(new StandardGetSpecOutput().withSpecification(connectorSpecification))));

    when(schedulerJobClient.createGetSpecJob(imageName)).thenReturn(job);

    assertDoesNotThrow(() -> validator.assertValidIntegrationImage(repo, tag));
  }

  @Test
  public void testThrowsOnInvalidImage() throws IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);
    when(schedulerJobClient.createGetSpecJob(imageName)).thenThrow(new IllegalArgumentException());

    assertThrows(KnownException.class, () -> validator.assertValidIntegrationImage(repo, tag));
  }

}
