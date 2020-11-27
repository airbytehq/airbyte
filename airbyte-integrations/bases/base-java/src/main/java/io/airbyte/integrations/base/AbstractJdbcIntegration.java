package io.airbyte.integrations.base;

import static org.jooq.impl.DSL.currentSchema;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcIntegration implements Integration {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcIntegration.class);

  private final String driverClass;
  private final SQLDialect dialect;

  public AbstractJdbcIntegration(final String driverClass, final SQLDialect dialect) {
    this.driverClass = driverClass;
    this.dialect = dialect;
  }

  public abstract JsonNode toJdbcConfig(JsonNode config);

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final Database database = getDatabase(config)) {
      // attempt to get current schema. this is a cheap query to sanity check that we can connect to the
      // database. `currentSchema()` is a jooq method that will run the appropriate query based on which
      // database it is connected to.
      database.query(this::getCurrentDatabaseName);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.debug("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Can't connect with provided configuration.");
    }
  }

  protected Database getDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass,
        dialect);
    }

  protected String getCurrentDatabaseName(DSLContext ctx) {
    return ctx.select(currentSchema()).fetch().get(0).getValue(0, String.class);
  }

}
