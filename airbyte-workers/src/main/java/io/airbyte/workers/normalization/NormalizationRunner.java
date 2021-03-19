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

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface NormalizationRunner extends AutoCloseable {

  /**
   * After this method is called, the caller must call close. Previous to this method being called a
   * NormalizationRunner can be instantiated and not worry about close being called.
   *
   * @throws Exception - any exception thrown from normalization will be handled gracefully by the
   *         caller.
   */
  default void start() throws Exception {
    // no-op.
  }

  /**
   * Executes normalization of the data in the destination.
   *
   * @param jobId - id of the job that launched normalization
   * @param attempt - current attempt
   * @param jobRoot - root dir available for the runner to use.
   * @param config - configuration for connecting to the destination
   * @param catalog - the schema of the json blob in the destination. it is used normalize the blob
   *        into typed columns.
   * @return true of normalization succeeded. otherwise false.
   * @throws Exception - any exception thrown from normalization will be handled gracefully by the
   *         caller.
   */
  boolean normalize(String jobId, int attempt, Path jobRoot, JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception;

  class NoOpNormalizationRunner implements NormalizationRunner {

    private static final Logger LOGGER = LoggerFactory.getLogger(NoOpNormalizationRunner.class);

    @Override
    public boolean normalize(String jobId, int attempt, Path jobRoot, JsonNode config, ConfiguredAirbyteCatalog catalog) {
      LOGGER.info("Running no op logger");
      return true;
    }

    @Override
    public void close() {
      // no op.
    }

  }

}
