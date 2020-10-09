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

import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(SingerIntegrationLauncher.class);

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  public SingerIntegrationLauncher(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public ProcessBuilder spec(Path jobRoot) throws WorkerException {
    return pbf.create(jobRoot, imageName, "--spec");
  }

  @Override
  public ProcessBuilder check(final Path jobRoot, final String configFilename) {
    throw new NotImplementedException("check doesn't exist for singer images");
  }

  @Override
  public ProcessBuilder discover(final Path jobRoot, final String configFilename) throws WorkerException {
    return pbf.create(jobRoot, imageName,
        "--config", configFilename,
        "--discover");
  }

  @Override
  public ProcessBuilder read(final Path jobRoot, final String configFilename, final String catalogFilename, final String stateFilename)
      throws WorkerException {
    String[] cmd = {
      "--config",
      configFilename,
      "--properties",
      catalogFilename
    };

    if (stateFilename != null) {
      cmd = ArrayUtils.addAll(cmd, "--state", stateFilename);
    }

    return pbf.create(jobRoot, imageName, cmd);
  }

  @Override
  public ProcessBuilder write(final Path jobRoot, final String configFilename, final String catalogFilename) throws WorkerException {
    return pbf.create(jobRoot, imageName, "--config", configFilename);
  }

}
