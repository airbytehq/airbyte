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

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import org.junit.jupiter.api.Test;

public class S3LogClientTest {

  @Test
  public void testMissingAwsCredentials() {
    var configs = mock(Configs.class);
    when(configs.getAwsAccessKey()).thenReturn("");
    when(configs.getAwsSecretAccessKey()).thenReturn("");

    assertThrows(RuntimeException.class, () -> new S3Logs().downloadCloudLog(configs, "this-path-should-not-matter"));
  }

  @Test
  public void testRetrieveAllLogs() throws IOException {
    var configs = new EnvConfigs();
    var data = new S3Logs().downloadCloudLog(configs, "logging-test");
    // TODO: Implement test.
    System.out.println(new String(Files.readAllBytes(data.toPath())));
  }

  /**
   * The test files for this test have been pre-generated and uploaded into the bucket folder. The
   * folder contains the following files with these contents:
   * <li>first-file.txt - Line 1, Line 2, Line 3</li>
   * <li>second-file.txt - Line 4, Line 5, Line 6</li>
   * <li>third-file.txt - Line 7, Line 8, Line 9</li>
   */
  @Test
  public void testTail() throws IOException {
    var configs = new EnvConfigs();
    var data = new S3Logs().tailCloudLog(configs, "logging-test/tail", 6);

    var expected = List.of("Line 4", "Line 5", "Line 6", "Line 7", "Line 8", "Line 9");
    assertEquals(data, expected);
  }

}
