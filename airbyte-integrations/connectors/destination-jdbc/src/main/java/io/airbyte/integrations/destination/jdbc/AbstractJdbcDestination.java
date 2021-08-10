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

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.SSHTunnel;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.sshd.client.SshClient;
import org.apache.sshd.client.session.ClientSession;

public abstract class AbstractJdbcDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcDestination.class);

  private final String driverClass;
  private final NamingConventionTransformer namingResolver;
  private final SqlOperations sqlOperations;

  protected String getDriverClass() {
    return driverClass;
  }

  protected NamingConventionTransformer getNamingResolver() {
    return namingResolver;
  }

  protected SqlOperations getSqlOperations() {
    return sqlOperations;
  }

  public AbstractJdbcDestination(final String driverClass,
                                 final NamingConventionTransformer namingResolver,
                                 final SqlOperations sqlOperations) {
    this.driverClass = driverClass;
    this.namingResolver = namingResolver;
    this.sqlOperations = sqlOperations;
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    SSHTunnel tunnelConfig = null;
    SshClient sshclient = null;
    ClientSession tunnelSession = null;
    try (final JdbcDatabase database = getDatabase(config)) {
      tunnelConfig = getSSHTunnelConfig(config);
      if (tunnelConfig.shouldTunnel()) {
        sshclient = tunnelConfig.createClient();
        LOGGER.error("JENNY TESTING - Client created.");
        tunnelSession = tunnelConfig.openTunnel(sshclient);
        LOGGER.error("JENNY TESTING - Tunnel opened.");
      }
      String outputSchema = namingResolver.getIdentifier(config.get("schema").asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, sqlOperations);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      if (tunnelConfig.shouldTunnel()) {
        try {
          if (sshclient != null) {
            tunnelConfig.closeTunnel(sshclient, tunnelSession);
          }
        } catch (Throwable t) {
          t.printStackTrace();
        }
      }
    }
  }

  public static void attemptSQLCreateAndDropTableOperations(String outputSchema,
                                                            JdbcDatabase database,
                                                            NamingConventionTransformer namingResolver,
                                                            SqlOperations sqlOps)
      throws Exception {
    // attempt to get metadata from the database as a cheap way of seeing if we can connect.
    database.bufferedResultSetQuery(conn -> conn.getMetaData().getCatalogs(), JdbcUtils::rowToJson);

    // verify we have write permissions on the target schema by creating a table with a random name,
    // then dropping that table
    String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
    sqlOps.createSchemaIfNotExists(database, outputSchema);
    sqlOps.createTableIfNotExists(database, outputSchema, outputTableName);
    sqlOps.dropTableIfExists(database, outputSchema, outputTableName);
  }

  protected JdbcDatabase getDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass);
  }



  protected SSHTunnel getSSHTunnelConfig(JsonNode config) {
    JsonNode ourConfig = config.get("tunnel_method");
    SSHTunnel sshconfig = new SSHTunnel(
        getConfigValueOrNull(ourConfig, "tunnel_method"),
        getConfigValueOrNull(ourConfig, "tunnel_host"),
        getConfigValueOrNull(ourConfig, "tunnel_ssh_port"),
        getConfigValueOrNull(ourConfig, "tunnel_username"),
        getConfigValueOrNull(ourConfig, "tunnel_usersshkey"),
        getConfigValueOrNull(ourConfig, "tunnel_userpass"),
        getConfigValueOrNull(ourConfig, "tunnel_db_remote_host"),
        getConfigValueOrNull(ourConfig, "tunnel_db_remote_port"),
        getConfigValueOrNull(ourConfig, "tunnel_localport")
    );
    java.security.Security.addProvider(
        new org.bouncycastle.jce.provider.BouncyCastleProvider()
    );
    return sshconfig;
  }

  private String getConfigValueOrNull(JsonNode config, String key) {
    return config != null && config.has(key) ? config.get(key).asText() : null;
  }

  public abstract JsonNode toJdbcConfig(JsonNode config);

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog, Consumer<AirbyteMessage> outputRecordCollector) {
    return JdbcBufferedConsumerFactory.create(outputRecordCollector, getDatabase(config), getSSHTunnelConfig(config), sqlOperations, namingResolver, config, catalog);
  }

}
