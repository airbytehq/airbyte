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

import io.airbyte.commons.io.IOs;
import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.utils.HttpClientUtils;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import okhttp3.OkHttpClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactoryPOC {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactoryPOC.class);
  // Explicitly create the underlying HTTP client since the Kube client has issues with closing the
  // client. It is not clear in which library the fault
  // lies. See https://github.com/fabric8io/kubernetes-client/issues/2403.
  private static final Config CONFIG = new ConfigBuilder().build();
  private static final OkHttpClient OK_HTTP_CLIENT = HttpClientUtils.createHttpClient(CONFIG);
  private static final KubernetesClient KUBE_CLIENT = new DefaultKubernetesClient(OK_HTTP_CLIENT, CONFIG);

  public static void main(String[] args) throws InterruptedException, IOException {
    LOGGER.info("Launching source process...");
    Process src = new KubePodProcess(KUBE_CLIENT, "src", "default", "np_source:dev", 9002, false);

    LOGGER.info("Launching destination process...");
    Process dest = new KubePodProcess(KUBE_CLIENT, "dest", "default", "np_dest:dev", 9003, true);

    LOGGER.info("Launching background thread to read destination lines...");
    ExecutorService executor = Executors.newSingleThreadExecutor();
    var listenTask = executor.submit(() -> {
      BufferedReader reader = new BufferedReader(new InputStreamReader(dest.getInputStream()));
      try {
        String line;
        while ((line = reader.readLine()) != null) {
          LOGGER.info("Destination sent: {}", line);
        }
      } catch (IOException e) {
        e.printStackTrace();
      }
    });

    LOGGER.info("Copying source stdout to destination stdin...");

    try (BufferedReader reader = IOs.newBufferedReader(src.getInputStream())) {
      try (PrintWriter writer = new PrintWriter(dest.getOutputStream(), true)) {
        String line;
        while ((line = reader.readLine()) != null) {
          writer.println(line);
        }
      }
    }

    LOGGER.info("Waiting for source process to terminate...");
    src.waitFor();
    LOGGER.info("Waiting for destination process to terminate...");
    dest.waitFor();

    LOGGER.info("Closing sync worker resources...");
    listenTask.cancel(true);
    executor.shutdownNow();
    // TODO(Davin): Figure out why these commands are not effectively shutting down OkHTTP even though
    // documentation suggests so. See
    // https://square.github.io/okhttp/4.x/okhttp/okhttp3/-ok-http-client/#shutdown-isnt-necessary
    // Instead, the pod shuts down after 5 minutes as the pool reaps the remaining idle connection after
    // 5 minutes of inactivity, as per the default configuration.
    OK_HTTP_CLIENT.dispatcher().executorService().shutdownNow();
    OK_HTTP_CLIENT.connectionPool().evictAll();
    KUBE_CLIENT.close();

    LOGGER.info("Done!");

    // Debug Statements, to remove both merging.
    LOGGER.info("src: {}", src.isAlive());
    LOGGER.info("dest: {}", dest.isAlive());
    LOGGER.info("executor terminated: {}", executor.isTerminated());
    LOGGER.info("executor shutdown: {}", executor.isShutdown());
    LOGGER.info("executor terminated: {}", executor.isTerminated());
    LOGGER.info("ok http client pool size: {}", OK_HTTP_CLIENT.connectionPool().connectionCount());
    LOGGER.info("ok http client pool idle size: {}", OK_HTTP_CLIENT.connectionPool().idleConnectionCount());
    LOGGER.info("ok http executor service shutdown: {}", OK_HTTP_CLIENT.dispatcher().executorService().isShutdown());

  }

}
