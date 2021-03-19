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
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(AirbyteIntegrationLauncher.class);

  private final String jobId;
  private final int attempt;
  private final String imageName;
  private final ProcessBuilderFactory pbf;

  public AirbyteIntegrationLauncher(long jobId, int attempt, final String imageName, final ProcessBuilderFactory pbf) {
    this(String.valueOf(jobId), attempt, imageName, pbf);
  }

  public AirbyteIntegrationLauncher(String jobId, int attempt, final String imageName, final ProcessBuilderFactory pbf) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public ProcessBuilder spec(final Path jobRoot) throws WorkerException {
    return pbf.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        "spec");
  }

  @Override
  public ProcessBuilder check(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        "check",
        "--config", configFilename);
  }

  @Override
  public ProcessBuilder discover(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        "discover",
        "--config", configFilename);
  }

  @Override
  public ProcessBuilder read(final Path jobRoot,
                             final String configFilename,
                             final String catalogFilename,
                             final String stateFilename)
      throws WorkerException {
    final List<String> arguments = Lists.newArrayList(
        "read",
        "--config", configFilename,
        "--catalog", catalogFilename);

    if (stateFilename != null) {
      arguments.add("--state");
      arguments.add(stateFilename);
    }

    return pbf.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        arguments);
  }

  @Override
  public ProcessBuilder write(Path jobRoot, String configFilename, String catalogFilename) throws WorkerException {
    return pbf.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        "write",
        "--config", configFilename,
        "--catalog", catalogFilename);
  }

}
