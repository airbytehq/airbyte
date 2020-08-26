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

package io.dataline.workers.singer;

import io.dataline.workers.Worker;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseSingerWorker<InputType, OutputType>
    implements Worker<InputType, OutputType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSingerWorker.class);

  protected void cancelHelper(Process workerProcess) {
    try {
      workerProcess.destroy();
      workerProcess.waitFor(10, TimeUnit.SECONDS);
      if (workerProcess.isAlive()) {
        workerProcess.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when cancelling job.", e);
    }
  }

  protected static String readFile(Path workspaceRoot, String fileName) {
    try {
      Path filePath = workspaceRoot.resolve(fileName);
      return FileUtils.readFileToString(filePath.toFile(), StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected static Path writeFile(Path workspaceRoot, String fileName, String contents) {
    try {
      Path filePath = workspaceRoot.resolve(fileName);
      FileUtils.writeStringToFile(filePath.toFile(), contents, StandardCharsets.UTF_8);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected static Path getFullPath(Path workspaceRoot, String fileName) {
    return workspaceRoot.resolve(fileName);
  }

  public static void main(String[] args) {
    writeFile(
        Path.of("/tmp/tests/dataline7245568476522994644/1/"),
        "config.json",
        "{\"password\":\"test\",\"dbname\":\"test\",\"port\":\"32841\",\"host\":\"172.17.0.1\",\"user\":\"test\"}");
  }
}
