package io.dataline.workers;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.async.ResultCallback;
import com.github.dockerjava.api.command.CreateContainerResponse;
import com.github.dockerjava.api.model.Frame;
import java.io.Closeable;
import java.io.IOException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerContainerRunner {

  private final static Logger LOGGER = LoggerFactory.getLogger(DockerContainerRunner.class);

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
      return new DockerContainerRunner(
          dockerClient,
          image
      );
    }
  }

  public DockerContainerRunner(DockerClient dockerClient, String image) {
    this.dockerClient = dockerClient;
    this.image = image;
  }

  public void run() {
    CreateContainerResponse container =
        dockerClient
            .createContainerCmd(image)
            .withStdInOnce()
            .exec();
    System.out.println(container);
    final CountDownLatch countDownLatch = new CountDownLatch(1);
    dockerClient
        .attachContainerCmd(container.getId())
        .withStdErr(true)
        .withStdOut(true)
        .exec(
            new ResultCallback<Frame>() {
              @Override
              public void close() throws IOException {
                System.out.println("close");
                countDownLatch.countDown();
              }

              @Override
              public void onStart(Closeable closeable) {
                System.out.println("onStart" + closeable);
              }

              @Override
              public void onNext(Frame object) {
                System.out.println("onNext" + object);
              }

              @Override
              public void onError(Throwable throwable) {
                System.out.println("onError" + throwable.getMessage());
                countDownLatch.countDown();
              }

              @Override
              public void onComplete() {
                System.out.println("onComplete");
                countDownLatch.countDown();
              }
            });

    dockerClient.startContainerCmd(container.getId()).exec();
    dockerClient.

    try {
      while (!countDownLatch.await(1, TimeUnit.SECONDS)) {
      }
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
  }

  public void awaitTermination(long timeout, TimeUnit timeUnit) {

  }

}
