/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcStressTest;
import java.sql.JDBCType;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;

@Disabled
public class MssqlStressTest extends JdbcStressTest {

  private MsSQLTestDatabase testdb;

  @BeforeEach
  public void setup() throws Exception {
    testdb = MsSQLTestDatabase.in(MsSQLTestDatabase.BaseImage.MSSQL_2022);
    super.setup();
  }

  @Override
  public Optional<String> getDefaultSchemaName() {
    return Optional.of("dbo");
  }

  @Override
  public JsonNode getConfig() {
    return testdb.testConfigBuilder().with("is_test", true).build();
  }

  @Override
  public AbstractJdbcSource<JDBCType> getSource() {
    return new MssqlSource();
  }

  @Override
  public String getDriverClass() {
    return MssqlSource.DRIVER_CLASS;
  }

}
