/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.databricks.utils.DatabricksConstants;
import io.airbyte.integrations.destination.databricks.utils.DatabricksDatabaseUtil;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import java.util.Collections;
import java.util.Map;
import javax.sql.DataSource;

public class DatabricksManagedTablesDestination extends AbstractJdbcDestination {

  public DatabricksManagedTablesDestination() {
    super(DatabricksConstants.DATABRICKS_DRIVER_CLASS, new DatabricksNameTransformer(), new DatabricksSqlOperations());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return DatabricksDatabaseUtil.getDataSource(config);
  }

}
