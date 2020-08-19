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
import com.github.dockerjava.api.async.ResultCallback.Adapter;
import com.github.dockerjava.api.command.AttachContainerCmd;
import com.github.dockerjava.api.command.CreateContainerCmd;
import com.github.dockerjava.api.command.CreateContainerResponse;
import com.github.dockerjava.api.model.Bind;
import com.github.dockerjava.api.model.Frame;
import com.github.dockerjava.api.model.HostConfig;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.google.common.collect.Lists;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerContainerRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerContainerRunner.class);

  private final DockerClient dockerClient;
  private final String image;

  public static class Builder {

    private final DockerClient dockerClient;

    private final String image;

    public Builder(DockerClient dockerClient, String image) {
      this.dockerClient = dockerClient;
      this.image = image;
    }

    public DockerContainerRunner build() {
      return new DockerContainerRunner(dockerClient, image);
    }
  }

  protected DockerContainerRunner(DockerClient dockerClient, String image) {
    this.dockerClient = dockerClient;
    this.image = image;
  }

  public void run(final List<String> args, final OutputStream oss, final InputStream iss)
      throws InterruptedException {
    CreateContainerCmd createContainerCmd =
        dockerClient
            .createContainerCmd(image)
            .withCmd(args)
            .withTty(false)
            .withHostConfig(
                HostConfig.newHostConfig().withBinds(Bind.parse("/tmp/singer:/tmp/abc")));
    if (iss != null) {
      createContainerCmd.withStdinOpen(true).withStdInOnce(true).withAttachStdin(true);
    }
    final CreateContainerResponse container = createContainerCmd.exec();
    LOGGER.debug("Container {} created ({})", container.getId(), image);

    dockerClient.startContainerCmd(container.getId()).exec();

    AttachContainerCmd attachContainerCmd =
        dockerClient.attachContainerCmd(container.getId()).withStdErr(true).withStdOut(true);

    if (iss != null) {
      attachContainerCmd.withStdIn(iss).withFollowStream(true);
    }
    Adapter<Frame> res =
        attachContainerCmd.exec(
            new Adapter<>() {
              @Override
              public void onNext(Frame object) {
                LOGGER.info("onNext {}: {}", container.getId(), object);
              }
            });

    BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(oss));

    try {
      for (long i = 0; i < 10; ++i) {
        writer.write("toto" + i + "\n");
        writer.flush();
        System.out.println(i);
      }
      oss.close();
      while (iss.available() > 0) {
        Thread.sleep(1000);
      }
      res.close();
      //      iss.close();

    } catch (IOException e) {
      e.printStackTrace();
    }
    //    TimeUnit.MINUTES.sleep(9999);

    dockerClient.waitContainerCmd(container.getId()).start().awaitStatusCode();
  }

  public boolean awaitTermination(long timeout, TimeUnit timeUnit) throws InterruptedException {
    return true;
  }

  public static void main(String[] args) throws InterruptedException, IOException {
    final DockerClient client =
        DockerClientImpl.getInstance(
            DefaultDockerClientConfig.createDefaultConfigBuilder().build(),
            new ApacheDockerHttpClient.Builder()
                .dockerHost(URI.create("unix:///var/run/docker.sock"))
                .build());

    PipedOutputStream pos = new PipedOutputStream();
    PipedInputStream pis = new PipedInputStream(pos);

    ByteArrayInputStream bais =
        new ByteArrayInputStream("toto\ntata\n".getBytes(StandardCharsets.UTF_8));

    DockerContainerRunner runnerDestination =
        //        new Builder(client, "dataline/integration-singer-csv-destination").build();
        new Builder(client, "busybox").build();
    runnerDestination.run(
        Lists.newArrayList("sh", "-c", "echo test > /tmp/abc/output2; cat -e >> /tmp/abc/output2"),
        pos,
        pis);
    //
    //    DockerContainerRunner runnerSource = new Builder(client, "busybox").build();
    //    runnerSource.run(
    //        Lists.newArrayList(
    //            "sh",
    //            "-c",
    //            "rm /tmp/abc/output; for i in 0 1 2 3 4 5 6 7 8 9; do echo test$i; done >>
    // /tmp/abc/output"),
    //        System.out,
    //        null);

    //    runnerSource.awaitTermination(1, TimeUnit.MINUTES);
    //    runnerDestination.awaitTermination(1, TimeUnit.MINUTES);
  }
}
