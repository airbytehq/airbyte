/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import java.sql.SQLType;
import java.sql.Types;

public enum PostgresType implements SQLType {

  BIT(Types.BIT),
  TINYINT(Types.TINYINT),
  SMALLINT(Types.SMALLINT),
  INTEGER(Types.INTEGER),
  BIGINT(Types.BIGINT),
  FLOAT(Types.FLOAT),
  REAL(Types.REAL),
  DOUBLE(Types.DOUBLE),
  NUMERIC(Types.NUMERIC),
  DECIMAL(Types.DECIMAL),
  CHAR(Types.CHAR),
  VARCHAR(Types.VARCHAR),
  LONGVARCHAR(Types.LONGVARCHAR),
  DATE(Types.DATE),
  TIME(Types.TIME),
  TIMESTAMP(Types.TIMESTAMP),
  BINARY(Types.BINARY),
  VARBINARY(Types.VARBINARY),
  LONGVARBINARY(Types.LONGVARBINARY),
  NULL(Types.NULL),
  OTHER(Types.OTHER),
  JAVA_OBJECT(Types.JAVA_OBJECT),
  DISTINCT(Types.DISTINCT),
  STRUCT(Types.STRUCT),
  ARRAY(Types.ARRAY),
  BLOB(Types.BLOB),
  CLOB(Types.CLOB),
  REF(Types.REF),
  DATALINK(Types.DATALINK),
  BOOLEAN(Types.BOOLEAN),
  ROWID(Types.ROWID),
  NCHAR(Types.NCHAR),
  NVARCHAR(Types.NVARCHAR),
  LONGNVARCHAR(Types.LONGNVARCHAR),
  NCLOB(Types.NCLOB),
  SQLXML(Types.SQLXML),
  REF_CURSOR(Types.REF_CURSOR),
  TIME_WITH_TIMEZONE(Types.TIME_WITH_TIMEZONE),
  TIMESTAMP_WITH_TIMEZONE(Types.TIMESTAMP_WITH_TIMEZONE),
  VARCHAR_ARRAY(Types.ARRAY),
  TEXT_ARRAY(Types.ARRAY),
  INTEGER_ARRAY(Types.ARRAY),
  NUMERIC_ARRAY(Types.ARRAY),
  TIMESTAMPTZ_ARRAY(Types.ARRAY),
  TIMESTAMP_ARRAY(Types.ARRAY),
  TIMETZ_ARRAY(Types.ARRAY),
  TIME_ARRAY(Types.ARRAY),
  DATE_ARRAY(Types.ARRAY),
  BIT_ARRAY(Types.ARRAY),
  BOOL_ARRAY(Types.ARRAY),
  NAME_ARRAY(Types.ARRAY),
  CHAR_ARRAY(Types.ARRAY),
  BPCHAR_ARRAY(Types.ARRAY),
  INT4_ARRAY(Types.ARRAY),
  INT2_ARRAY(Types.ARRAY),
  INT8_ARRAY(Types.ARRAY),
  MONEY_ARRAY(Types.ARRAY),
  OID_ARRAY(Types.ARRAY),
  FLOAT4_ARRAY(Types.ARRAY),
  FLOAT8_ARRAY(Types.ARRAY),
  BYTEA_ARRAY(Types.ARRAY);

  /**
   * The Integer value for the JDBCType. It maps to a value in {@code Types.java}
   */
  private Integer type;

  /**
   * Constructor to specify the data type value from {@code Types) for
   * this data type. @param type The value from {@code Types) for this data type
   */
  PostgresType(final Integer type) {
    this.type = type;
  }

  /**
   * {@inheritDoc }
   *
   * @return The name of this {@code SQLType}.
   */
  public String getName() {
    return name();
  }

  /**
   * Returns the name of the vendor that supports this data type.
   *
   * @return The name of the vendor for this data type which is {@literal java.sql} for JDBCType.
   */
  public String getVendor() {
    return "java.sql";
  }

  /**
   * Returns the vendor specific type number for the data type.
   *
   * @return An Integer representing the data type. For {@code JDBCType}, the value will be the same
   *         value as in {@code Types} for the data type.
   */
  public Integer getVendorTypeNumber() {
    return type;
  }

  /**
   * Returns the {@code JDBCType} that corresponds to the specified {@code Types} value
   *
   * @param type {@code Types} value
   * @return The {@code JDBCType} constant
   * @throws IllegalArgumentException if this enum type has no constant with the specified
   *         {@code Types} value
   * @see Types
   */
  public static PostgresType valueOf(int type) {
    for (PostgresType sqlType : PostgresType.class.getEnumConstants()) {
      if (type == sqlType.type)
        return sqlType;
    }
    throw new IllegalArgumentException("Type:" + type + " is not a valid "
        + "Types.java value.");
  }

  public static PostgresType safeGetJdbcType(final int columnTypeInt) {
    try {
      return PostgresType.valueOf(columnTypeInt);
    } catch (final Exception e) {
      return PostgresType.VARCHAR;
    }
  }

}
