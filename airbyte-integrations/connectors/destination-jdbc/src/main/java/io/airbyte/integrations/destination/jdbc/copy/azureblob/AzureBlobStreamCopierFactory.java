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

package io.airbyte.integrations.destination.jdbc.copy.azureblob;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;

public abstract class AzureBlobStreamCopierFactory implements StreamCopierFactory<AzureBlobConfig> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(String configuredSchema,
                             AzureBlobConfig azureBlobConfig,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase db,
                             SqlOperations sqlOperations) {
    try {
      AirbyteStream stream = configuredStream.getStream();
      DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
      String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      String streamName = stream.getName();
      AppendBlobClient appendBlobClient = AzureBlobStreamCopier.getAppendBlobClient(azureBlobConfig, streamName);

      return create(stagingFolder, syncMode, schema, streamName, appendBlobClient, db, azureBlobConfig, nameTransformer, sqlOperations);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * For specific copier suppliers to implement.
   */
  public abstract StreamCopier create(String stagingFolder,
                                      DestinationSyncMode syncMode,
                                      String schema,
                                      String streamName,
                                      AppendBlobClient appendBlobClient,
                                      JdbcDatabase db,
                                      AzureBlobConfig azureBlobConfig,
                                      ExtendedNameTransformer nameTransformer,
                                      SqlOperations sqlOperations)
      throws Exception;

}
