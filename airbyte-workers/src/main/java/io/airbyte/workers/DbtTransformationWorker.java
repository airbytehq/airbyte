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

import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DbtTransformationWorker implements Worker<OperatorDbtInput, Void> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationWorker.class);

  private final String jobId;
  private final int attempt;
  private final DbtTransformationRunner dbtTransformationRunner;
  private final ResourceRequirements resourceRequirements;

  private final AtomicBoolean cancelled;

  public DbtTransformationWorker(final String jobId,
                                 final int attempt,
                                 ResourceRequirements resourceRequirements,
                                 DbtTransformationRunner dbtTransformationRunner) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.dbtTransformationRunner = dbtTransformationRunner;
    this.resourceRequirements = resourceRequirements;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public Void run(OperatorDbtInput operatorDbtInput, Path jobRoot) throws WorkerException {
    long startTime = System.currentTimeMillis();

    try (dbtTransformationRunner) {
      LOGGER.info("Running dbt transformation.");
      dbtTransformationRunner.start();
      final Path transformRoot = Files.createDirectories(jobRoot.resolve("transform"));
      if (!dbtTransformationRunner.run(
          jobId,
          attempt,
          transformRoot,
          operatorDbtInput.getDestinationConfiguration(),
          resourceRequirements,
          operatorDbtInput.getOperatorDbt())) {
        throw new WorkerException("DBT Transformation Failed.");
      }
    } catch (Exception e) {
      throw new WorkerException("Dbt Transformation Failed.", e);
    }
    if (cancelled.get()) {
      LOGGER.info("Dbt Transformation was cancelled.");
    }

    final Duration duration = Duration.ofMillis(System.currentTimeMillis() - startTime);
    LOGGER.info("Dbt Transformation executed in {}.", duration.toMinutesPart());

    return null;
  }

  @Override
  public void cancel() {
    LOGGER.info("Cancelling Dbt Transformation runner...");
    try {
      cancelled.set(true);
      dbtTransformationRunner.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

}
