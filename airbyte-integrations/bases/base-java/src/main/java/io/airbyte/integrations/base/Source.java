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

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import java.util.stream.Stream;

// todo (cgardens) - share common parts of this interface with source.
public interface Source extends Integration {

  /**
   * Discover the current schema in the source.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @return Description of the schema.
   * @throws Exception - any exception.
   */
  AirbyteCatalog discover(JsonNode config) throws Exception;

  /**
   * Return a stream of messages pulled from the source.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @param state - state of the incoming messages.
   * @return Stream that produces message. The stream will be consumed until no records remain.
   *         {@link Stream#close()} will always be called once regardless of success or failure.
   * @throws Exception - any exception.
   */
  Stream<AirbyteMessage> read(JsonNode config, AirbyteCatalog catalog, JsonNode state) throws Exception;

}
