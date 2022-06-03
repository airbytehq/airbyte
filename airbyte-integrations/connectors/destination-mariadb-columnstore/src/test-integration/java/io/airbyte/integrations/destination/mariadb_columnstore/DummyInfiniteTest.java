package io.airbyte.integrations.destination.mariadb_columnstore;

import java.time.LocalDateTime;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

public class DummyInfiniteTest {

  private ExecutorService executorService;

  @Test
  public void test() throws InterruptedException {

    executorService = Executors.newFixedThreadPool(1);
    executorService.submit(() -> {
      while (true) {
        System.out.println(LocalDateTime.now());
        System.out.println(" \t Free Memory \t Total Memory \t Max Memory");
        System.out.println("\t " + Runtime.getRuntime().freeMemory() +
            " \t \t " + Runtime.getRuntime().totalMemory() +
            " \t \t   " + Runtime.getRuntime().maxMemory());
        Thread.sleep(10000);
      }
    });
     executorService.awaitTermination(4, TimeUnit.HOURS);

  }

}
