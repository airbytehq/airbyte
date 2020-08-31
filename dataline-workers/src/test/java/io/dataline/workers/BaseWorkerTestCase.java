/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.io.Resources;
import io.dataline.commons.json.Jsons;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@SuppressWarnings("PMD.AbstractClassWithoutAbstractMethod")
public abstract class BaseWorkerTestCase {

  // TODO inject via env
  protected Path workspaceRoot;
  protected ProcessBuilderFactory pbf;

  @BeforeAll
  public void init() throws IOException {
    final Path testsPath = Path.of("/tmp/tests");
    Files.createDirectories(testsPath);
    this.workspaceRoot = Files.createTempDirectory(testsPath, "dataline");
    this.pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "host");

    System.out.println("Workspace directory: " + workspaceRoot.toString());
  }

  protected Path createJobRoot(String jobId) throws IOException {
    final Path jobRoot = workspaceRoot.resolve(jobId);
    return Files.createDirectories(jobRoot);
  }

  protected String readResource(String name) throws IOException {
    URL resource = Resources.getResource(name);
    return Resources.toString(resource, Charset.defaultCharset());
  }

  protected <T> T readResource(final String name, final Class<T> klass) throws IOException {
    return Jsons.deserialize(readResource(name), klass);
  }

  protected void assertJsonEquals(final String s1, final String s2) {
    assertEquals(Jsons.deserialize(s1), Jsons.deserialize(s2));
  }

}
