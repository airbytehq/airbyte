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

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.io.Resources;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
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

  protected String readResource(String name) {
    URL resource = Resources.getResource(name);
    try {
      return Resources.toString(resource, Charset.defaultCharset());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected void assertJsonEquals(String s1, String s2) throws IOException {
    ObjectMapper mapper = new ObjectMapper();
    assertEquals(mapper.readTree(s1), mapper.readTree(s2));
  }

  protected <T> T getJsonAsTyped(String file, Class<T> clazz) {
    final URL resource = Resources.getResource(file);
    final ObjectMapper objectMapper = new ObjectMapper();
    try {
      return objectMapper.readValue(new File(resource.getFile()), clazz);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
