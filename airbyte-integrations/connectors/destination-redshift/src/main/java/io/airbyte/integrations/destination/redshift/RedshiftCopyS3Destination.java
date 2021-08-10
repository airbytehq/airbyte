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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

/**
 * A more efficient Redshift Destination than the sql-based {@link RedshiftDestination}. Instead of
 * inserting data as batched SQL INSERTs, we follow Redshift best practices and, 1) Stream the data
 * to S3. One compressed file is created per table. 2) Copy the S3 file to Redshift. See
 * https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-use-copy.html for more info.
 *
 * Although Redshift recommends splitting the file for more efficient copying, this introduces
 * complexity around file partitioning that should be handled by a file destination connector. The
 * single file approach is orders of magnitude faster than batch inserting and 'good-enough' for
 * now.
 */
public class RedshiftCopyS3Destination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        getS3Config(config),
        catalog,
        new RedshiftStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(JsonNode config) throws Exception {
    S3StreamCopier.attemptS3WriteAndDelete(getS3Config(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) throws Exception {
    var jdbcConfig = RedshiftInsertDestination.getJdbcConfig(config);
    return Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        RedshiftInsertDestination.DRIVER_CLASS);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new RedshiftSqlOperations();
  }

  private String getConfiguredSchema(JsonNode config) {
    return config.get("schema").asText();
  }

  private S3Config getS3Config(JsonNode config) {
    return S3Config.getS3Config(config);
  }

}
