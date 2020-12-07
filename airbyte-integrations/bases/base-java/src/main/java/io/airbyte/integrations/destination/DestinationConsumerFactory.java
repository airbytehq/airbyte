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

package io.airbyte.integrations.destination;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;

/**
 * This factory builds pipelines of DestinationConsumer of AirbyteMessage with different strategies.
 */
public class DestinationConsumerFactory {

  /**
   * This pipeline is based on DestinationConsumers that can interact with some kind of Sql based
   * database destinations.
   *
   * The Strategy used here is:
   * <p>
   * 1. Create a temporary table for each stream
   * </p>
   * <p>
   * 2. Accumulate records in a buffer. One buffer per stream.
   * </p>
   * <p>
   * 3. As records accumulate write them in batch to the database. We set a minimum numbers of records
   * before writing to avoid wasteful record-wise writes.
   * </p>
   * <p>
   * 4. Once all records have been written to buffer, flush the buffer and write any remaining records
   * to the database (regardless of how few are left).
   * </p>
   * <p>
   * 5. In a single transaction, delete the target tables if they exist and rename the temp tables to
   * the final table name.
   * </p>
   *
   * @param destination is a destination based on Sql engine which provides certain SQL Queries to
   *        interact with
   * @param namingResolver is a SQLNamingResolvable object to translate strings into valid identifiers
   *        supported by the underlying Sql Database
   * @param config the destination configuration object
   * @param catalog describing the streams of messages to write to the destination
   * @return A DestinationConsumer able to accept the Airbyte Messages
   * @throws Exception
   */
  public static DestinationConsumer<AirbyteMessage> build(SqlDestinationOperations destination,
                                                          IdentifierNamingResolvable namingResolver,
                                                          JsonNode config,
                                                          ConfiguredAirbyteCatalog catalog)
      throws Exception {
    final Map<String, DestinationWriteContext> writeConfigs =
        new DestinationWriteContextFactory(namingResolver).build(config, catalog);
    // Step 2, 3 & 4
    DestinationConsumerStrategy buffer = new BufferedStreamConsumer(destination, catalog);
    // Step 5
    TmpToFinalTable commit = new TruncateInsertIntoConsumer(destination);
    // Step 1 then orchestrate buffering strategy and commit if success
    DestinationConsumerStrategy result = new TmpDestinationConsumer(destination, buffer, commit);
    result.setContext(writeConfigs);
    return result;
  }

}
