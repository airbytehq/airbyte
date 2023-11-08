/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.util.LinkedHashMap;

/**
 * A record representing the {@link java.sql.ResultSet} returned by calling
 * {@link DatabaseMetaData#getTypeInfo()}
 * <p>
 * See that method for a better description of the parameters to this record
 */
public record TypeInfoRecordSet(
                                String typeName,
                                int dataType,
                                int precision,
                                String literalPrefix,
                                String literalSuffix,
                                String createParams,
                                short nullable,
                                boolean caseSensitive,
                                short searchable,
                                boolean unsignedAttribute,
                                boolean fixedPrecScale,
                                boolean autoIncrement,
                                String localTypeName,
                                short minimumScale,
                                short maximumScale,

                                // Unused
                                int sqlDataType,

                                // Unused
                                int sqlDatetimeSub,
                                int numPrecRadix) {

  public static LinkedHashMap<String, TypeInfoRecordSet> getTypeInfoList(final DatabaseMetaData databaseMetaData) throws Exception {
    final ResultSet rs = databaseMetaData.getTypeInfo();
    final LinkedHashMap<String, TypeInfoRecordSet> types = new LinkedHashMap<>();
    while (rs.next()) {
      final var typeName = rs.getString("TYPE_NAME");
      types.put(typeName,
          new TypeInfoRecordSet(
              typeName,
              rs.getInt("DATA_TYPE"),
              rs.getInt("PRECISION"),
              rs.getString("LITERAL_PREFIX"),
              rs.getString("LITERAL_SUFFIX"),
              rs.getString("CREATE_PARAMS"),
              rs.getShort("NULLABLE"),
              rs.getBoolean("CASE_SENSITIVE"),
              rs.getShort("SEARCHABLE"),
              rs.getBoolean("UNSIGNED_ATTRIBUTE"),
              rs.getBoolean("FIXED_PREC_SCALE"),
              rs.getBoolean("AUTO_INCREMENT"),
              rs.getString("LOCAL_TYPE_NAME"),
              rs.getShort("MINIMUM_SCALE"),
              rs.getShort("MAXIMUM_SCALE"),
              rs.getInt("SQL_DATA_TYPE"),
              rs.getInt("SQL_DATETIME_SUB"),
              rs.getInt("NUM_PREC_RADIX")));
    }
    return types;
  }

}
