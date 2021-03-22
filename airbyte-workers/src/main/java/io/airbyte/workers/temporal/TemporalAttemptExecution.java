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

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.EnvConfigs;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.BiConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * This class represents a single run of a worker. It handles making sure the correct inputs and
 * outputs are passed to the selected worker. It also makes sures that the outputs of the worker are
 * persisted to the db.
 */
public class TemporalAttemptExecution<T> implements CheckedSupplier<T, TemporalJobException> {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalAttemptExecution.class);

  private final Path jobRoot;
  private final CheckedFunction<Path, T, Exception> execution;
  private final String jobId;
  private final BiConsumer<Path, String> mdcSetter;
  private final CheckedConsumer<Path, IOException> jobRootDirCreator;

  @VisibleForTesting
  TemporalAttemptExecution(Path workspaceRoot, JobRunConfig jobRunConfig, CheckedFunction<Path, T, Exception> execution) {
    this(workspaceRoot, jobRunConfig, execution, WorkerUtils::setJobMdc, Files::createDirectories);
  }

  public TemporalAttemptExecution(Path workspaceRoot,
                                  JobRunConfig jobRunConfig,
                                  CheckedFunction<Path, T, Exception> execution,
                                  BiConsumer<Path, String> mdcSetter,
                                  CheckedConsumer<Path, IOException> jobRootDirCreator) {
    this.jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    this.execution = execution;
    this.jobId = jobRunConfig.getJobId();
    this.mdcSetter = mdcSetter;
    this.jobRootDirCreator = jobRootDirCreator;
  }

  @Override
  public T get() throws TemporalJobException {
    try {
      mdcSetter.accept(jobRoot, jobId);

      LOGGER.info("Executing worker wrapper. Airbyte version: {}", new EnvConfigs().getAirbyteVersionOrWarning());
      jobRootDirCreator.accept(jobRoot);

      return execution.apply(jobRoot);
    } catch (TemporalJobException e) {
      throw e;
    } catch (Exception e) {
      throw new TemporalJobException(jobRoot.resolve(WorkerConstants.LOG_FILENAME), e);
    }
  }

}
