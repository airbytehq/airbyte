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
import com.github.dockerjava.api.command.AttachContainerCmd;
import com.github.dockerjava.api.command.CreateContainerCmd;
import com.github.dockerjava.api.command.CreateContainerResponse;
import com.github.dockerjava.api.model.Frame;
import com.github.dockerjava.api.model.StreamType;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.zerodep.ZerodepDockerHttpClient;
import com.google.common.collect.Lists;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.net.URI;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerContainerRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerContainerRunner.class);

  private final DockerClient dockerClient;
  private final String image;

  private final CountDownLatch countDownLatch;

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

    countDownLatch = new CountDownLatch(1);
  }

  public void run(final List<String> args, final OutputStream oss, final InputStream iss) {
    CreateContainerCmd createContainerCmd = dockerClient.createContainerCmd(image).withCmd(args);
    if (iss != null) {
      createContainerCmd.withStdinOpen(true);
    }
    final CreateContainerResponse container = createContainerCmd.exec();
    LOGGER.debug("Container {} created ({})", container.getId(), image);

    AttachContainerCmd attachContainerCmd =
        dockerClient
            .attachContainerCmd(container.getId())
            .withStdErr(true)
            .withStdOut(true)
            .withFollowStream(true);

    if (iss != null) {
      attachContainerCmd.withStdIn(iss);
    }

    attachContainerCmd.exec(
        new ResultCallback<Frame>() {
          @Override
          public void close() throws IOException {
            LOGGER.info("close {}", container.getId());
            IOUtils.closeQuietly(iss, io -> {});
            IOUtils.closeQuietly(oss, io -> {});
            countDownLatch.countDown();
          }

          @Override
          public void onStart(Closeable closeable) {
            LOGGER.info("onStart {}: {}", container.getId(), closeable);
          }

          @Override
          public void onNext(Frame object) {
            LOGGER.info("onNext {}: {}", container.getId(), object);
            try {
              if (object.getStreamType() == StreamType.STDOUT) {
                oss.write(object.getPayload());
              }
            } catch (IOException e) {
              LOGGER.error("Error while piping", e);
            }
          }

          @Override
          public void onError(Throwable throwable) {
            LOGGER.info("onError {}: {}", container.getId(), throwable);
            IOUtils.closeQuietly(iss, io -> {});
            IOUtils.closeQuietly(oss, io -> {});
            countDownLatch.countDown();
          }

          @Override
          public void onComplete() {
            LOGGER.info("onComplete {}", container.getId());
            IOUtils.closeQuietly(iss, io -> {});
            IOUtils.closeQuietly(oss, io -> {});
            countDownLatch.countDown();
          }
        });
    dockerClient.startContainerCmd(container.getId()).exec();
  }

  public boolean awaitTermination(long timeout, TimeUnit timeUnit) throws InterruptedException {
    return countDownLatch.await(timeout, timeUnit);
  }

  public static void main(String[] args) throws InterruptedException, IOException {
    final DockerClient client =
        DockerClientImpl.getInstance(
            DefaultDockerClientConfig.createDefaultConfigBuilder().build(),
            new ZerodepDockerHttpClient.Builder()
                .dockerHost(URI.create("unix:///var/run/docker.sock"))
                .build());

    PipedOutputStream pos = new PipedOutputStream();
    PipedInputStream pis = new PipedInputStream(pos);

    DockerContainerRunner runnerDestination =
        new Builder(client, "dataline/integration-singer-csv-destination").build();
    runnerDestination.run(Lists.newArrayList(), System.out, pis);

    DockerContainerRunner runnerSource =
        new Builder(client, "dataline/integration-singer-exchangerateapi_io-source").build();
    runnerSource.run(Lists.newArrayList(), pos, null);

    runnerSource.awaitTermination(1, TimeUnit.MINUTES);
    runnerDestination.awaitTermination(1, TimeUnit.MINUTES);
  }
}
