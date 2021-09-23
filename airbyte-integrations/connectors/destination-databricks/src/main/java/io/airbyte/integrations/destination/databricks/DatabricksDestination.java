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

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class DatabricksDestination extends CopyDestination {

  public DatabricksDestination() {
    super("database_schema");
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new DatabricksDestination()).run(args);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog, Consumer<AirbyteMessage> outputRecordCollector) {
    DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        databricksConfig,
        catalog,
        new DatabricksStreamCopierFactory(),
        databricksConfig.getDatabaseSchema());
  }

  @Override
  public void checkPersistence(JsonNode config) {
    DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    S3StreamCopier.attemptS3WriteAndDelete(databricksConfig.getS3DestinationConfig().getS3Config());
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new DatabricksNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode jsonConfig) {
    return getDatabase(DatabricksDestinationConfig.get(jsonConfig));
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

  static String getDatabricksConnectionString(DatabricksDestinationConfig databricksConfig) {
    return String.format("jdbc:spark://%s:%s/default;transportMode=http;ssl=1;httpPath=%s;UserAgentEntry=Airbyte",
        databricksConfig.getDatabricksServerHostname(),
        databricksConfig.getDatabricksPort(),
        databricksConfig.getDatabricksHttpPath());
  }

  static JdbcDatabase getDatabase(DatabricksDestinationConfig databricksConfig) {
    return Databases.createJdbcDatabase(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(),
        getDatabricksConnectionString(databricksConfig),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS);
  }

}
