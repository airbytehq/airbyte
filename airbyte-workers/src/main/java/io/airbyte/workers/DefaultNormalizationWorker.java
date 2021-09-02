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

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.NormalizationInput;
import io.airbyte.workers.normalization.NormalizationRunner;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationWorker implements NormalizationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationWorker.class);

  private final String jobId;
  private final int attempt;
  private final NormalizationRunner normalizationRunner;

  private final AtomicBoolean cancelled;

  public DefaultNormalizationWorker(final String jobId,
                                    final int attempt,
                                    final NormalizationRunner normalizationRunner) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.normalizationRunner = normalizationRunner;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public Void run(NormalizationInput input, Path jobRoot) throws WorkerException {
    long startTime = System.currentTimeMillis();

    try (normalizationRunner) {
      LOGGER.info("Running normalization.");
      normalizationRunner.start();

      Path normalizationRoot = null;
      // There are no shared volumes on Kube; only create this for Docker.
      if (new EnvConfigs().getWorkerEnvironment().equals(WorkerEnvironment.DOCKER)) {
        normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
      }

      if (!normalizationRunner.normalize(jobId, attempt, normalizationRoot, input.getDestinationConfiguration(), input.getCatalog(),
          input.getResourceRequirements())) {
        throw new WorkerException("Normalization Failed.");
      }
    } catch (Exception e) {
      throw new WorkerException("Normalization Failed.", e);
    }

    if (cancelled.get()) {
      LOGGER.info("Normalization was cancelled.");
    }

    final Duration duration = Duration.ofMillis(System.currentTimeMillis() - startTime);
    LOGGER.info("Normalization executed in {}.", duration.toMinutesPart());

    return null;
  }

  @Override
  public void cancel() {
    LOGGER.info("Cancelling normalization runner...");
    try {
      cancelled.set(true);
      normalizationRunner.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

}
