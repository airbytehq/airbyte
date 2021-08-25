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
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.io.File;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksDestination.class);

  public static final String DRIVER_CLASS = "com.simba.spark.jdbc.Driver";

  // TODO: this isn't working yet!
  public static void getDriver() throws MalformedURLException, ClassNotFoundException {
    File driverJar = new File("/Users/phlair/Downloads/SparkDriver/SparkJDBC42.jar");
    URL jarUrl = new URL("jar", "", "file:" + driverJar.getAbsolutePath() + "!/");
    URLClassLoader myLoader = new URLClassLoader(new URL[] { jarUrl } );
    myLoader.loadClass(DRIVER_CLASS);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {

    try (final JdbcDatabase database = getDatabase(config)) {
      DatabricksSqlOperations databricksSqlOperations = (DatabricksSqlOperations) getSqlOperations();

      String outputSchema = getNamingResolver().getIdentifier(config.get("database").asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, getNamingResolver(), databricksSqlOperations);

      databricksSqlOperations.verifyLocalFileEnabled(database);

      // TODO: enforce databricks runtime version instead of this mySql code
//      VersionCompatibility compatibility = dbSqlOperations.isCompatibleVersion(database);
//      if (!compatibility.isCompatible()) {
//        throw new RuntimeException(String
//            .format("Your MySQL version %s is not compatible with Airbyte",
//                compatibility.getVersion()));
//      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  public DatabricksDestination() {
    super(DRIVER_CLASS, new DatabricksNameTransformer(), new DatabricksSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode databricksConfig) {
    return getJdbcConfig(databricksConfig);
  }

  public static JsonNode getJdbcConfig(JsonNode databricksConfig) {
    final String schema = Optional.ofNullable(databricksConfig.get("schema")).map(JsonNode::asText).orElse("default");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", "dummy")
        .put("password", "dummy")
//        .put("jdbc_url", String.format("jdbc:TODO://%s:%s/%s",
//            databricksConfig.get("host").asText(),
//            databricksConfig.get("port").asText(),
//            databricksConfig.get("database").asText()))
//        .put("schema", schema)
        .put("jdbc_url", databricksConfig.get("jdbcUrl").asText())
        .build());
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting destination: {}", DatabricksDestination.class);
    getDriver();
    new IntegrationRunner(new DatabricksDestination()).run(args);
    LOGGER.info("completed destination: {}", DatabricksDestination.class);
  }

}
