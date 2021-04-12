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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class AirbyteIntegrationLauncherTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";

  private ProcessBuilderFactory pbf;
  private AirbyteIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    pbf = Mockito.mock(ProcessBuilderFactory.class);
    launcher = new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, FAKE_IMAGE, pbf);
  }

  @Test
  void spec() throws WorkerException {
    launcher.spec(JOB_ROOT);

    Mockito.verify(pbf).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, "spec");
  }

  @Test
  void check() throws WorkerException {
    launcher.check(JOB_ROOT, "config");

    Mockito.verify(pbf).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE,
        "check",
        "--config", "config");
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "config");

    Mockito.verify(pbf).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE,
        "discover",
        "--config", "config");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "catalog", "state");

    Mockito.verify(pbf).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE,
        Lists.newArrayList(
            "read",
            "--config", "config",
            "--catalog", "catalog",
            "--state", "state"));
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, "config", "catalog");

    Mockito.verify(pbf).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE,
        "write",
        "--config", "config",
        "--catalog", "catalog");
  }

}
