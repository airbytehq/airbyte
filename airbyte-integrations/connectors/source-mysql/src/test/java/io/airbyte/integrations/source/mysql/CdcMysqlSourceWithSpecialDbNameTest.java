/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import org.testcontainers.containers.MySQLContainer;

public class CdcMysqlSourceWithSpecialDbNameTest extends CdcMysqlSourceTest {

  @Override
  protected MySQLTestDatabase createTestDatabase() {
    var container = new MySQLContainerFactory().shared(
        BaseImage.MYSQL_8.reference,
        ContainerModifier.INVALID_TIMEZONE_CEST.methodName,
        ContainerModifier.CUSTOM_NAME.methodName);
    return new TestDatabaseWithInvalidDatabaseName(container)
        .initialized()
        .withCdcPermissions();
  }

  static class TestDatabaseWithInvalidDatabaseName extends MySQLTestDatabase {

    public static final String INVALID_DB_NAME = "invalid@name";

    public TestDatabaseWithInvalidDatabaseName(MySQLContainer<?> container) {
      super(container);
    }

    @Override
    public String getDatabaseName() {
      return withNamespace(INVALID_DB_NAME);
    }

  }

}
