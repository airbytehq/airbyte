/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import java.sql.SQLType;
import java.sql.Types;
import java.util.Arrays;

public enum SingleStoreType implements SQLType {

  VARCHAR("VARCHAR", Types.VARCHAR),
  BIGINT("BIGINT", Types.BIGINT),
  BIGINT_UNSIGNED("BIGINT UNSIGNED", Types.BIGINT),
  FLOAT("FLOAT", Types.REAL),
  FLOAT_UNSIGNED("FLOAT UNSIGNED", Types.REAL),
  DOUBLE("DOUBLE", Types.DOUBLE),
  DOUBLE_UNSIGNED("DOUBLE UNSIGNED", Types.DOUBLE),
  DECIMAL("DECIMAL", Types.DECIMAL),
  DECIMAL_UNSIGNED("DECIMAL UNSIGNED", Types.DECIMAL),
  TINYINT("TINYINT", Types.TINYINT),
  TINYINT_UNSIGNED("TINYINT UNSIGNED", Types.TINYINT),
  SMALLINT("SMALLINT", Types.SMALLINT),
  SMALLINT_UNSIGNED("SMALLINT UNSIGNED", Types.SMALLINT),
  INT("INT", Types.INTEGER),
  INT_UNSIGNED("INT UNSIGNED", Types.INTEGER),
  MEDIUMINT("MEDIUMINT", Types.INTEGER),
  MEDIUMINT_UNSIGNED("MEDIUMINT UNSIGNED", Types.INTEGER),
  LONGTEXT("LONGTEXT", Types.LONGVARCHAR),
  VARBINARY("VARBINARY", Types.VARBINARY),
  JSON("JSON", Types.LONGVARCHAR),
  DATETIME("DATETIME", Types.TIMESTAMP),
  TIMESTAMP("TIMESTAMP", Types.TIMESTAMP),
  TEXT("TEXT", Types.LONGVARCHAR),
  MEDIUMTEXT("MEDIUMTEXT", Types.LONGVARCHAR),
  SET("SET", Types.VARCHAR),
  ENUM("ENUM", Types.VARCHAR),
  TINYBLOB("TINYBLOB", Types.VARBINARY),
  BLOB("BLOB", Types.LONGVARBINARY),
  MEDIUMBLOB("MEDIUMBLOB", Types.LONGVARBINARY),
  LONGBLOB("LONGBLOB", Types.LONGVARBINARY),
  BIT("BIT", Types.BIT),
  DATE("DATE", Types.DATE),
  TIME("TIME", Types.TIME),
  YEAR("YEAR", Types.INTEGER),
  CHAR("CHAR", Types.CHAR),
  BINARY("BINARY", Types.BINARY),
  TINYTEXT("TINYTEXT", Types.VARCHAR),
  GEOGRAPHYPOINT("GEOGRAPHYPOINT", Types.OTHER),
  GEOGRAPHY("GEOGRAPHY", Types.OTHER),
  VECTOR("VECTOR", Types.OTHER),
  NULL("NULL", Types.NULL);

  SingleStoreType(String singleStoreTypeName, int type) {
    this.singleStoreTypeName = singleStoreTypeName;
    this.type = type;
  }

  private final String singleStoreTypeName;
  private final int type;

  public static SingleStoreType getByName(String name) {
    return Arrays.stream(values()).filter(v -> v.getName().equalsIgnoreCase(name)).findFirst()
        .orElseThrow(() -> new IllegalArgumentException(
            "Type:" + name + " is not a valid."));
  }

  @Override
  public String getName() {
    return singleStoreTypeName;
  }

  @Override
  public String getVendor() {
    return "com.singlestore";
  }

  @Override
  public Integer getVendorTypeNumber() {
    return type;
  }

}
