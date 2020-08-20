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

import static java.util.concurrent.TimeUnit.MINUTES;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.async.ResultCallback;
import com.github.dockerjava.api.async.ResultCallback.Adapter;
import com.github.dockerjava.api.command.AttachContainerCmd;
import com.github.dockerjava.api.command.CreateContainerCmd;
import com.github.dockerjava.api.command.CreateContainerResponse;
import com.github.dockerjava.api.model.Bind;
import com.github.dockerjava.api.model.Frame;
import com.github.dockerjava.api.model.HostConfig;
import com.github.dockerjava.api.model.StreamType;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.google.common.collect.Lists;
import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
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
            .withHostConfig(
                HostConfig.newHostConfig().withBinds(Bind.parse("/tmp/singer:/tmp/abc")));

    // If we have streams configured, lets prepare the container to be attached
    streams.getStdout().ifPresent(noop -> createContainerCmd.withAttachStdout(true));
    streams.getStderr().ifPresent(noop -> createContainerCmd.withAttachStderr(true));
    streams
        .getStdin()
        .ifPresent(
            noop ->
                createContainerCmd.withStdinOpen(true).withStdInOnce(true).withAttachStdin(true));

    final String containerId = createContainerCmd.exec().getId();
    LOGGER.debug("Container {} created (image: {})", containerId, image);

    final AttachContainerCmd attachContainerCmd = dockerClient.attachContainerCmd(containerId);
    attachContainerCmd.withFollowStream(true);

    // Attach streams if necessary
    streams.getStdout().ifPresent(noop -> attachContainerCmd.withStdOut(true));
    streams.getStderr().ifPresent(noop -> attachContainerCmd.withStdErr(true));
    streams.getStdin().ifPresent(attachContainerCmd::withStdIn);

    Adapter<Frame> res = attachContainerCmd.exec(new FrameAdapter(containerId, streams));

    dockerClient.startContainerCmd(containerId).exec();
    LOGGER.debug("Container {} started", containerId);

    return new DockerContainerHandle(res);
  }

  private static class FrameAdapter extends Adapter<Frame> {

    private final String containerId;
    private final StdStreams streams;

    public FrameAdapter(String containerId, StdStreams streams) {
      this.containerId = containerId;
      this.streams = streams;
    }

    @Override
    public void onStart(Closeable stream) {
      System.out.println(stream);
      super.onStart(stream);
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

  public static class DockerContainerHandle {

    public final Adapter<Frame> callback;

    private DockerContainerHandle(ResultCallback.Adapter<Frame> callback) {
      this.callback = callback;
    }

    public boolean awaitCompletion(long timeout, TimeUnit timeUnit) throws InterruptedException {
      return callback.awaitCompletion(timeout, timeUnit);
    }
  }

  public static void main(String[] args) throws InterruptedException, IOException {
    DockerClient client =
        DockerClientImpl.getInstance(
            DefaultDockerClientConfig.createDefaultConfigBuilder().build(),
            new ApacheDockerHttpClient.Builder()
                .dockerHost(URI.create("unix:///var/run/docker.sock"))
                .build());

    //    testSimpleOut(client);
    //    testSimpleErr(client);
    testProvidedIn(client);
    //    testSimpleIn(client);

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
  }

  public static void fakeAssert(boolean condition, String message) {
    if (!condition) {
      throw new IllegalStateException(message);
    }
  }

  public static void testSimpleOut(DockerClient client) throws InterruptedException {
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams streams = new StdStreams(baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    runnerSource
        .run(Lists.newArrayList("echo", "abc"), streams)
        .awaitCompletion(1, TimeUnit.MINUTES);

    fakeAssert(baosOut.toString().equals("abc\n"), "Should be equal to abc");
    fakeAssert(baosErr.toString().isEmpty(), "Should be empty");
    System.out.println("baosOut = " + baosOut.toString());
    System.out.println("baosErr = " + baosErr.toString());
  }

  public static void testSimpleErr(DockerClient client) throws InterruptedException {
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();
    final ByteArrayOutputStream baosErr = new ByteArrayOutputStream();
    final StdStreams streams = new StdStreams(baosOut, baosErr);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    runnerSource
        .run(Lists.newArrayList("sh", "-c", "a2bc"), streams)
        .awaitCompletion(1, TimeUnit.MINUTES);

    fakeAssert(baosOut.toString().isEmpty(), "Should be empty");
    fakeAssert(baosErr.toString().equals("sh: a2bc: not found\n"), "Should be equal to the error");
    System.out.println("baosOut = " + baosOut.toString());
    System.out.println("baosErr = " + baosErr.toString());
  }

  public static void testSimpleIn(DockerClient client) throws InterruptedException, IOException {
    final PipedOutputStream pos = new PipedOutputStream();
    final PipedInputStream pis = new PipedInputStream(pos);
    final ByteArrayOutputStream baosOut = new ByteArrayOutputStream();

    final StdStreams streams = new StdStreams(pis, baosOut, null);

    DockerContainerRunner runnerSource = new DockerContainerRunner(client, "busybox");
    DockerContainerHandle handle = runnerSource.run(Lists.newArrayList("cat", "-e"), streams);

    for (int i = 0; i < 999; i++) {
      pos.write("abcd\n".getBytes(StandardCharsets.UTF_8));
    }
    pos.flush();
    pis.close();

    //    handle.awaitCompletion(1, TimeUnit.MINUTES);
    handle.callback.close();
    pos.close();

    System.out.println("baosOut = " + baosOut.toString());
  }

  public static class AttachContainerTestCallback extends ResultCallback.Adapter<Frame> {

    private StringBuffer log = new StringBuffer();

    @Override
    public void onNext(Frame item) {
      log.append(new String(item.getPayload()));
      super.onNext(item);
    }

    @Override
    public String toString() {
      return log.toString();
    }
  }

  private static void testProvidedIn(DockerClient dockerClient)
      throws IOException, InterruptedException {

    String snippet = "hello world";

    CreateContainerResponse container =
        dockerClient
            .createContainerCmd("busybox")
            .withCmd("cat", "-e")
            .withTty(false)
            .withStdinOpen(true)
            .withStdInOnce(true)
            .exec();

    LOGGER.info("Created container: {}", container.toString());

    final AtomicReference<Closeable> streamRef = new AtomicReference<>();
    AttachContainerTestCallback callback =
        new AttachContainerTestCallback() {
          @Override
          public void onStart(Closeable stream) {
            System.out.println(stream);
            streamRef.set(stream);
            super.onStart(stream);
          }
        };

    try (PipedOutputStream out = new PipedOutputStream();
        PipedInputStream in = new PipedInputStream(out)) {

      dockerClient.startContainerCmd(container.getId()).exec();

      dockerClient
          .attachContainerCmd(container.getId())
          .withStdErr(true)
          .withStdOut(true)
          .withFollowStream(true)
          .withStdIn(in)
          .exec(callback);

      out.write((snippet + "\n").getBytes());
      out.flush();
      //      streamRef.get().close();
      callback.awaitCompletion(15, MINUTES);
      callback.close();
    }
    System.out.println(callback.toString());
  }
}
