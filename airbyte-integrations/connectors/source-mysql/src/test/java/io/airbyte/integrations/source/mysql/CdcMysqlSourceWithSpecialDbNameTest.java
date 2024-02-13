/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;

public class CdcMysqlSourceWithSpecialDbNameTest extends CdcMysqlSourceTest {

  public static final String INVALID_DB_NAME = "invalid@name";

  @Override
  protected MySQLTestDatabase createTestDatabase() {
    return MySQLTestDatabase.inWithDbName(BaseImage.MYSQL_8, INVALID_DB_NAME, ContainerModifier.INVALID_TIMEZONE_CEST, ContainerModifier.CUSTOM_NAME)
        .withCdcPermissions();
  }

}
