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

package io.airbyte.workers.process;

import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodList;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactoryPOC {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactoryPOC.class);

  private static final KubernetesClient KUBE_CLIENT = new DefaultKubernetesClient();

  // todo: this should really be cached
  public static String getCommandFromImage(String imageName) throws IOException {
    final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

    final String podName = "airbyte-command-fetcher-" + suffix;

    final List<String> cmd =
        Lists.newArrayList(
            "kubectl",
            "run",
//            "--generator=run-pod/v1",
            // "--rm",
            "-i",
            "--pod-running-timeout=24h",
            "--image=" + imageName,
            "--command=true",
            "--restart=Never",
            podName,
            "--",
            "sh",
            "-c",
            "echo \"AIRBYTE_ENTRYPOINT=$AIRBYTE_ENTRYPOINT\"");

    Process start = new ProcessBuilder(cmd).start();

    try (BufferedReader reader = IOs.newBufferedReader(start.getInputStream())) {
      String line;
      while ((line = reader.readLine()) != null && !line.contains("AIRBYTE_ENTRYPOINT"));

      if (line == null || !line.contains("AIRBYTE_ENTRYPOINT")) {
        throw new RuntimeException("Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
      } else {
        String[] splits = line.split("=", 2);
        if (splits.length == 1) {
          throw new RuntimeException(
              "Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
        } else {
          return splits[1];
        }
      }
    }
  }

  private static void saveJaredWork() {
    try {
      // todo: test this with args that are used by the process
      Process process = new KubeProcessBuilderFactory(Path.of("stdout_template.yaml"))
          .create(0L, 0, Path.of("/tmp"), "np_source:dev", null)
          .start();

      process.getOutputStream().write(100);
      process.getInputStream().read();

      // after running this main:
      // kubectl port-forward airbyte-worker-0-0-fmave 9000:9000
      // socat -d -d -d TCP-LISTEN:9000,bind=127.0.0.1 stdout

      LOGGER.info("waiting...");
      int code = process.waitFor();
      LOGGER.info("code = " + code);
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
      e.printStackTrace();
    }
  }

  public static String getPodIP(String podName) {
    // TODO: Why does directly searching for the pod not work?
    // LOGGER.info(destPod.getStatus().getPodIP());
    // destPod = client.resource(destPod).get();
    // LOGGER.info("Status: {}", destPod.getStatus());
    // LOGGER.info("IP: {}", destPod.getStatus().getPodIP());
    // IP = destPod.getStatus().getPodIP();

    // TODO: We could assign labels to pods to narrow the search.
    PodList pods = KUBE_CLIENT.pods().inNamespace("default").list();
    for (Pod p : pods.getItems()) {
      // Filter by pod and retrieve IP.
      if (p.getMetadata().getName().equals(podName)) {
        LOGGER.info("Found IP!");
        return p.getStatus().getPodIP();
      }
    }

    return null;
  }

  public static void main(String[] args) throws InterruptedException, IOException {
    LOGGER.info("Launching source process...");
    Process src = new KubePodProcess(KUBE_CLIENT, "src", "np_source:dev", 9002, false);

    LOGGER.info("Launching destination process...");
    Process dest = new KubePodProcess(KUBE_CLIENT, "dest", "np_dest:dev", 9003, true);

    LOGGER.info("Launching background thread to read destination lines...");
    ExecutorService executor = Executors.newSingleThreadExecutor();
    executor.submit(() -> {
      BufferedReader reader = new BufferedReader(new InputStreamReader(dest.getInputStream()));

      while (true) {
        try {
          String line;
          if ((line = reader.readLine()) != null) {
            LOGGER.info("Destination sent: {}", line);
          }
        } catch (IOException e) {
          e.printStackTrace();
        }
      }
    });

    LOGGER.info("Copying source stdout to destination stdin...");

    BufferedReader reader = IOs.newBufferedReader(src.getInputStream());
    PrintWriter writer = new PrintWriter(dest.getOutputStream(), true);

    String line;
    while ((line = reader.readLine()) != null) {
      writer.println(line);
    }
    writer.close();

    LOGGER.info("Waiting for source...");
    src.waitFor();
    LOGGER.info("Waiting for destination...");
    dest.waitFor();
    LOGGER.info("Done!");

    System.exit(0); // todo: handle executors so we don't need to kill the JVM
  }

}
