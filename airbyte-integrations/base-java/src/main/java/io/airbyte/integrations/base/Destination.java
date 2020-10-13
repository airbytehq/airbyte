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
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.singer.SingerMessage;

// todo (cgardens) - share common parts of this interface with source.
public interface Destination {

  /**
   * Fetch the specification for the integration.
   *
   * @return specification.
   * @throws Exception - any exception.
   */
  ConnectorSpecification spec() throws Exception;

  /**
   * Check whether, given the current configuration, the integration can connect to the destination.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @return Whether or not the connection was successful. Optional message if it was not.
   * @throws Exception - any exception.
   */
  StandardCheckConnectionOutput check(JsonNode config) throws Exception;

  /**
   * Discover the current schema in the destination.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @return Description of the schema.
   * @throws Exception - any exception.
   */
  StandardDiscoverCatalogOutput discover(JsonNode config) throws Exception;

  /**
   * Return a consumer that writes messages to the destination.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param schema - schema of the incoming messages.
   * @return Consumer that accepts message. The {@link DestinationConsumer#accept(Object)} will be
   *         called n times where n is the number of messages. {@link DestinationConsumer#complete()}
   *         will be called once if all messages were accepted successfully.
   *         {@link DestinationConsumer#close()} will always be called once regardless of success or
   *         failure.
   * @throws Exception - any exception.
   */
  DestinationConsumer<SingerMessage> write(JsonNode config, Schema schema) throws Exception;

}
