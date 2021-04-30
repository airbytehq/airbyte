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

package io.airbyte.integrations.destination.redshift;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftCopyConsumer<T> extends CopyConsumer<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftCopyConsumer.class);
  protected static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;

  public RedshiftCopyConsumer(String configuredSchema,
                              T config,
                              ConfiguredAirbyteCatalog catalog,
                              JdbcDatabase db,
                              StreamCopierFactory<T> streamCopierFactory,
                              SqlOperations sqlOperations,
                              ExtendedNameTransformer nameTransformer) {
    super(configuredSchema, config, catalog, db, streamCopierFactory, sqlOperations, nameTransformer);
  }

  @Override
  protected boolean isValidData(final AirbyteStreamNameNamespacePair streamName, final String data) {
    final int dataSize = data.getBytes().length;
    if (dataSize > REDSHIFT_VARCHAR_MAX_BYTE_SIZE) {
      LOGGER.warn("Data({}) from stream {} exceeds limit of VARCHAR(65535) on Redshift... Ignoring record", dataSize, streamName);
      return false;
    }
    return true;
  }

}
