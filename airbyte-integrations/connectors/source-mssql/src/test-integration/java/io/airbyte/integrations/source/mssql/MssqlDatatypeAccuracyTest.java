/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import org.junit.jupiter.api.Disabled;

@Disabled
public class MssqlDatatypeAccuracyTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in(MsSQLTestDatabase.BaseImage.MSSQL_2022);
    return testdb.getDatabase();
  }

  @Override
  protected void initTests() {
    for (final JDBCType t : JDBCType.values()) {
      switch (t) {
        case BIT -> {
          addDataTypeTestData(
              TestDataHolder.builder()
                  .sourceType(t.name())
                  .airbyteType(JsonSchemaType.BOOLEAN)
                  .fullSourceDataType(t.getName())
                  .build());
        }
        default -> throw new IllegalStateException("Unexpected value: " + t);
      }
    }
  }

  @Override
  public void testDataContent() throws Exception {}

  @Override
  public boolean testCatalog() {
    return true;
  }

}
