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
import org.apache.commons.lang3.NotImplementedException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class SingerIntegrationLauncherTest {

  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";

  private ProcessBuilderFactory pbf;
  private SingerIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    pbf = Mockito.mock(ProcessBuilderFactory.class);
    launcher = new SingerIntegrationLauncher(FAKE_IMAGE, pbf);
  }

  @Test
  void spec() throws WorkerException {
    launcher.spec(JOB_ROOT);

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE, "--spec");
  }

  @Test
  void check() {
    Assertions.assertThrows(
        NotImplementedException.class,
        () -> launcher.check(JOB_ROOT, "abc"));
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "abc");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "--config", "abc",
        "--discover");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "catalog", "state");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "--config", "config",
        "--properties", "catalog",
        "--state", "state");
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, "config");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE, "--config", "config");
  }

}
