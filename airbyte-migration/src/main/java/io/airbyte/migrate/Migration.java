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

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public interface Migration {

  /**
   * The Airbyte Version associated with this migration. This string must be unique across all
   * migration. This string is never used as a sort key.
   *
   * @return version
   */
  String getVersion();

  /**
   * Returns a map of the relative path of the file resource within the input archive to the
   * JsonSchema associated with the records that will be received as input for this migration. If
   * records do not match these schemas, the migration will fail.
   *
   * @return map
   */
  Map<ResourceId, JsonNode> getInputSchema();

  /**
   * Returns a map of the relative path of the file resource within the output archive to the
   * JsonSchema associated with the records that will be output for this resource in migration. If
   * records do not match theses schemas, the migration will fail.
   *
   * @return map
   */
  Map<ResourceId, JsonNode> getOutputSchema();

  /**
   * Execute migration.
   *
   * @param inputData Map of the relative path of the file resource within the input archive to a
   *        stream of its records.
   * @param outputData Map of the relative path of the file resource within the output archive to a
   *        consumer that takes the transformed records.
   */
  void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData);

}
