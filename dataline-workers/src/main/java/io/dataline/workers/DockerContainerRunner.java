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
import com.github.dockerjava.api.async.ResultCallback;
import com.github.dockerjava.api.async.ResultCallback.Adapter;
import com.github.dockerjava.api.command.AttachContainerCmd;
import com.github.dockerjava.api.command.CreateContainerCmd;
import com.github.dockerjava.api.model.Bind;
import com.github.dockerjava.api.model.Frame;
import com.github.dockerjava.api.model.HostConfig;
import com.github.dockerjava.api.model.StreamType;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.google.common.collect.Lists;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.net.URI;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerContainerRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerContainerRunner.class);

  private final DockerClient dockerClient;
  private final String image;

  public static class StdStreams {

    private final InputStream stdin;
    private final OutputStream stdout;
    private final OutputStream stderr;

    public StdStreams(OutputStream stdout, OutputStream stderr) {
      this(null, stdout, stderr);
    }

    public StdStreams(PipedInputStream stdin, OutputStream stdout, OutputStream stderr) {
      this.stdin = stdin;
      this.stdout = stdout;
      this.stderr = stderr;
    }

    public Optional<InputStream> getStdin() {
      return Optional.ofNullable(stdin);
    }

    public Optional<OutputStream> getStdout() {
      return Optional.ofNullable(stdout);
    }

    public Optional<OutputStream> getStderr() {
      return Optional.ofNullable(stderr);
    }
  }

  public DockerContainerRunner(DockerClient dockerClient, String image) {
    this.dockerClient = dockerClient;
    this.image = image;
  }

  public DockerContainerHandle run(final List<String> args, final StdStreams streams) {
    final CreateContainerCmd createContainerCmd =
        dockerClient
            .createContainerCmd(image)
            .withCmd(args)
            .withTty(false)
            .withAttachStdout(true)
            .withHostConfig(
                HostConfig.newHostConfig().withBinds(Bind.parse("/tmp/singer:/tmp/abc")));

    // If we have stdin configured, lets prepare the container to receive stdin
    streams
        .getStdin()
        .ifPresent(
            noop -> {
              createContainerCmd.withStdinOpen(true).withStdInOnce(true).withAttachStdin(true);
            });

    final String containerId = createContainerCmd.exec().getId();
    LOGGER.debug("Container {} created (image: {})", containerId, image);

    final AttachContainerCmd attachContainerCmd = dockerClient.attachContainerCmd(containerId);
    // Attach streams if necessary
    streams
        .getStdout()
        .ifPresent(noop -> attachContainerCmd.withStdOut(true) /*.withFollowStream(true)*/);
    streams
        .getStderr()
        .ifPresent(noop -> attachContainerCmd.withStdErr(true) /*.withFollowStream(true)*/);
    streams
        .getStdin()
        .ifPresent(iss -> attachContainerCmd.withStdIn(iss) /*.withFollowStream(true)*/);

    Adapter<Frame> res = attachContainerCmd.exec(new FrameAdapter(containerId, streams));

    return new DockerContainerHandle(res);
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

    //
    //    System.out.println("streams = " + streams.getStdin().get().available());
    //
    //    dockerClient.startContainerCmd(containerId).exec();
    //    LOGGER.debug("Container {} started", containerId);
    //
    //    for (int i = 0; i < 1; i++) {
    //      StringBuilder sb = new StringBuilder();
    //      sb.append("toto").append(i).append("\n");
    //      streams.getStdout().get().write(sb.toString().getBytes(StandardCharsets.UTF_8));
    //    }
    //
    //    streams.getStdout().get().close();
    //
    //    res.awaitCompletion(10, TimeUnit.SECONDS);
    //    dockerClient.waitContainerCmd(containerId).start().awaitStatusCode();

    final PipedOutputStream pos = new PipedOutputStream();
    final PipedInputStream pis = new PipedInputStream(pos);

    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams top = new StdStreams(pis, baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    DockerContainerHandle handle = runnerSource.run(Lists.newArrayList("cat", "-e"), top);

    System.out.println("baisInput.available() = " + pis.available());
    System.out.println("baosOut.toString() = " + baosOut.toString());
    System.out.println("baosErr.toString() = " + baosErr.toString());

    //    PipedOutputStream pos = new PipedOutputStream();
    //    PipedInputStream pis = new PipedInputStream(pos);
    //
    //    ByteArrayInputStream bais =
    //        new ByteArrayInputStream("toto\ntata\n".getBytes(StandardCharsets.UTF_8));
    //
    //    DockerContainerRunner runnerDestination =
    //        //        new Builder(client, "dataline/integration-singer-csv-destination").build();
    //        new Builder(client, "busybox").build();
    //    runnerDestination.run(
    //        Lists.newArrayList("sh", "-c", "echo test > /tmp/abc/output2; cat -e >>
    // /tmp/abc/output2"),
    //        pos,
    //        pis);
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

    //
    //    BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(oss));
    //
    //    try {
    //      for (long i = 0; i < 999; ++i) {
    //        writer.write("toto" + i + "\n");
    //        writer.flush();
    //        System.out.println(i);
    //      }
    //      oss.close();
    //      //      while (iss.available() > 0) {
    //      //        Thread.sleep(1000);
    //      //      }
    //      res.awaitCompletion(10, TimeUnit.SECONDS);
    //      res.close();
    //      //      iss.close();
    //
    //    } catch (IOException e) {
    //      e.printStackTrace();
    //    }
    //    //    TimeUnit.MINUTES.sleep(9999);
    //
    //    dockerClient.waitContainerCmd(containerId).start().awaitStatusCode();
  }

  public static class DockerContainerHandle {

    private final Adapter<Frame> callback;

    private DockerContainerHandle(ResultCallback.Adapter<Frame> callback) {
      this.callback = callback;
    }

    public boolean awaitCompletion(long timeout, TimeUnit timeUnit) throws InterruptedException {
      return callback.awaitCompletion(timeout, timeUnit);
    }
  }

  private static class FrameAdapter extends Adapter<Frame> {

    private final String containerId;
    private final StdStreams streams;

    public FrameAdapter(String containerId, StdStreams streams) {
      this.containerId = containerId;
      this.streams = streams;
    }

    @Override
    public void onNext(Frame object) {
      LOGGER.info("onNext {}: {}", containerId, object);
      try {
        if (object.getStreamType() == StreamType.STDOUT && streams.getStdout().isPresent()) {
          streams.getStdout().get().write(object.getPayload());
        } else if (object.getStreamType() == StreamType.STDERR && streams.getStderr().isPresent()) {
          streams.getStderr().get().write(object.getPayload());
        }
      } catch (IOException e) {
        LOGGER.error("Error while processing frame");
      }
    }
  }
}
