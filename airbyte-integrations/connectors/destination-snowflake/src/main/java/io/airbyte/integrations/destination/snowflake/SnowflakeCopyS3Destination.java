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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.Copier;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumer;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Copier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopierSupplier;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;

public class SnowflakeCopyS3Destination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    return new CopyConsumer(getConfiguredSchema(config), getS3Config(config), catalog, getDatabase(config), this::getCopier, getSqlOperations(),
        getNameTransformer());
  }

  @Override
  public void attemptWriteToPersistence(JsonNode config) {
    S3Copier.attemptWriteToPersistence(getS3Config(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new SnowflakeSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) {
    return SnowflakeDatabase.getDatabase(config);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new SnowflakeSqlOperations();
  }

  private Copier getCopier(String configuredSchema,
                           S3Config s3Config,
                           String stagingFolder,
                           DestinationSyncMode destinationSyncMode,
                           AirbyteStream airbyteStream,
                           ExtendedNameTransformer nameTransformer,
                           JdbcDatabase jdbcDatabase,
                           SqlOperations sqlOperations) {
    return new S3CopierSupplier(SnowflakeS3Copier::new).get(configuredSchema, s3Config, stagingFolder, destinationSyncMode, airbyteStream,
        nameTransformer,
        jdbcDatabase, sqlOperations);
  }

  private String getConfiguredSchema(JsonNode config) {
    return config.get("schema").asText();
  }

  private S3Config getS3Config(JsonNode config) {
    final JsonNode loadingMethod = config.get("loading_method");
    return new S3Config(
        loadingMethod.get("s3_bucket_name").asText(),
        loadingMethod.get("access_key_id").asText(),
        loadingMethod.get("secret_access_key").asText(),
        null);
  }

}
