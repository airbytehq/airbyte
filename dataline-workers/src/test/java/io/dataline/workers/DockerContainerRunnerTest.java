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

package io.dataline.workers;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.google.common.collect.Lists;
import io.dataline.workers.DockerContainerRunner.StdStreams;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.URI;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class DockerContainerRunnerTest {

  private static DockerClient client;

  @BeforeAll
  static void beforeAll() {
    client =
        DockerClientImpl.getInstance(
            DefaultDockerClientConfig.createDefaultConfigBuilder().build(),
            new ApacheDockerHttpClient.Builder()
                .dockerHost(URI.create("unix:///var/run/docker.sock"))
                .build());
  }

  @Test
  void testWriteToStdOut() throws InterruptedException {
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams streams = new StdStreams(baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    runnerSource
        .run(Lists.newArrayList("echo", "abc"), streams)
        .awaitCompletion(1, TimeUnit.MINUTES);

    Assertions.assertEquals("abc", baosOut.toString());
    Assertions.assertTrue(baosErr.toString().isEmpty());
  }

  @Test
  void testWriteToStdErr() throws InterruptedException, IOException {
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams streams = new StdStreams(null, baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    runnerSource.run(Lists.newArrayList("sh", "-c", "abc"), streams);

    Assertions.assertEquals("abc", baosOut.toString());
    Assertions.assertTrue(baosErr.toString().isEmpty());
  }

  @Test
  void testReadInput() throws InterruptedException, IOException {
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams streams = new StdStreams(null, baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    runnerSource.run(Lists.newArrayList("sh", "-c", "abc"), streams);

    Assertions.assertEquals("abc", baosOut.toString());
    Assertions.assertTrue(baosErr.toString().isEmpty());
  }
}
