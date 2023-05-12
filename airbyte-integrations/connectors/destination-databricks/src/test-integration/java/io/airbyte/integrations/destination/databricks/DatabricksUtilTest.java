/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.integrations.destination.databricks.utils.DatabricksConstants;
import io.airbyte.integrations.destination.databricks.utils.DatabricksDatabaseUtil;
import java.sql.SQLException;
import java.util.Map;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksUtilTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksUtilTest.class);

  /**
   * Magic Databricks JDBC param. This param exists because of issue with fetching data via SELECT. It
   * produces next error: Error occured while deserializing arrow data: sun.misc.Unsafe or
   * java.nio.DirectByteBuffer.<init>(long, int) not available databricks. This solution was
   * accidentally found here (But it is not related to the error above)
   * https://community.databricks.com/s/question/0D58Y00009AHCDSSA5/jdbc-driver-support-for-openjdk-17.
   * But no idea what it does, but it fixed the issue. NOTE: Only for integration tests
   */
  // TODO: Investigate what EnableArrow=0 does
  private static final Map<String, String> DEFAULT_PROPERTY = Map.of("EnableArrow", "0");

  protected static DSLContext getDslContext(final DatabricksDestinationConfig databricksConfig) {
    return DSLContextFactory.create(DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.personalAccessToken(), DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        DatabricksDatabaseUtil.getDatabricksConnectionString(databricksConfig), SQLDialect.DEFAULT, DEFAULT_PROPERTY);
  }

  protected static void cleanUpData(final DatabricksDestinationConfig databricksConfig) throws SQLException {
    LOGGER.info("Dropping database schema {}", databricksConfig.schema());
    try (final DSLContext dslContext = DatabricksUtilTest.getDslContext(databricksConfig)) {
      final Database database = new Database(dslContext);
      // we cannot use jooq dropSchemaIfExists method here because there is no proper dialect for
      // Databricks, and it incorrectly quotes the schema name
      database
          .query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s.%s CASCADE;", databricksConfig.catalog(), databricksConfig.schema())));
    } catch (final Exception e) {
      throw new SQLException(e);
    }
  }

}
