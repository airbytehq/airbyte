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

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.InputStream;

public abstract class GcsStreamCopierFactory implements StreamCopierFactory<GcsConfig> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(final String configuredSchema,
                             final GcsConfig gcsConfig,
                             final String stagingFolder,
                             final DestinationSyncMode syncMode,
                             final AirbyteStream stream,
                             final ExtendedNameTransformer nameTransformer,
                             final JdbcDatabase db,
                             final SqlOperations sqlOperations) {
    try {
      final var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      final var schema = getSchema(stream, configuredSchema, nameTransformer);

      final InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
      final GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
      final Storage storageClient = StorageOptions.newBuilder()
          .setCredentials(credentials)
          .setProjectId(gcsConfig.getProjectId())
          .build()
          .getService();

      return create(stagingFolder, syncMode, schema, pair.getName(), storageClient, db, gcsConfig, nameTransformer, sqlOperations);
    } catch (final Exception e) {
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
                                      Storage storageClient,
                                      JdbcDatabase db,
                                      GcsConfig gcsConfig,
                                      ExtendedNameTransformer nameTransformer,
                                      SqlOperations sqlOperations)
      throws Exception;

  private String getSchema(final AirbyteStream stream, final String configuredSchema, final ExtendedNameTransformer nameTransformer) {
    if (stream.getNamespace() != null) {
      return nameTransformer.convertStreamName(stream.getNamespace());
    } else {
      return nameTransformer.convertStreamName(configuredSchema);
    }
  }

}
