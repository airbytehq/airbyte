/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

/**
 * Note that MySQL documentation discusses about identifiers case sensitivity using the
 * lower_case_table_names system variable. As one of their recommendation is: "It is best to adopt a
 * consistent convention, such as always creating and referring to databases and tables using
 * lowercase names. This convention is recommended for maximum portability and ease of use.
 *
 * Source: https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html"
 *
 * As a result, we are here forcing all identifier (table, schema and columns) names to lowercase.
 */
public class MySQLNameTransformer extends ExtendedNameTransformer {

  // These constants must match those in destination_name_transformer.py
  public static final int MAX_MYSQL_NAME_LENGTH = 64;
  // DBT appends a suffix to table names
  public static final int TRUNCATE_DBT_RESERVED_SIZE = 12;
  // 4 charachters for 1 underscore and 3 suffix (e.g. _ab1)
  // 4 charachters for 1 underscore and 3 schema hash
  public static final int TRUNCATE_RESERVED_SIZE = 8;
  public static final int TRUNCATION_MAX_NAME_LENGTH = MAX_MYSQL_NAME_LENGTH - TRUNCATE_DBT_RESERVED_SIZE - TRUNCATE_RESERVED_SIZE;

  @Override
  public String getIdentifier(String name) {
    String identifier = applyDefaultCase(super.getIdentifier(name));
    return truncateName(identifier, TRUNCATION_MAX_NAME_LENGTH);
  }

  @Override
  public String getTmpTableName(String streamName) {
    String tmpTableName = applyDefaultCase(super.getTmpTableName(streamName));
    return truncateName(tmpTableName, TRUNCATION_MAX_NAME_LENGTH);
  }

  @Override
  public String getRawTableName(String streamName) {
    String rawTableName = applyDefaultCase(super.getRawTableName(streamName));
    return truncateName(rawTableName, TRUNCATION_MAX_NAME_LENGTH);
  }

  static String truncateName(String name, int maxLength) {
    if (name.length() <= maxLength) {
      return name;
    }

    int allowedLength = maxLength - 2;
    String prefix = name.substring(0, allowedLength / 2);
    String suffix = name.substring(name.length() - allowedLength / 2);
    return prefix + "__" + suffix;
  }

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
