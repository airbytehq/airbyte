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

package io.airbyte.workers;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultGetSpecWorker implements GetSpecWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecWorker.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private Process process;

  public DefaultGetSpecWorker(final IntegrationLauncher integrationLauncher, AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultGetSpecWorker(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorSpecification run(JobGetSpecConfig config, Path jobRoot) throws WorkerException {
    try {
      process = integrationLauncher.spec(jobRoot).start();

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      Optional<ConnectorSpecification> spec;
      try (InputStream stdout = process.getInputStream()) {
        spec = streamFactory.create(IOs.newBufferedReader(stdout))
            .filter(message -> message.getType() == Type.SPEC)
            .map(AirbyteMessage::getSpec)
            .findFirst();

        // todo (cgardens) - let's pre-fetch the images outside of the worker so we don't need account for
        // this.
        // retrieving spec should generally be instantaneous, but since docker images might not be pulled
        // it could take a while longer depending on internet conditions as well.
        WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
      }

      int exitCode = process.exitValue();
      if (exitCode == 0) {
        if (spec.isEmpty()) {
          throw new WorkerException("integration failed to output a spec struct.");
        }

        return spec.get();

      } else {
        throw new WorkerException(String.format("Spec job subprocess finished with exit code %s", exitCode));
      }
    } catch (Exception e) {
      throw new WorkerException(String.format("Error while getting spec from image %s: %s", config.getDockerImage(), e));
    }

  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
