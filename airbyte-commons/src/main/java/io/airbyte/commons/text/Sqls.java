/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.text;

import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

public class Sqls {

  public static <T extends Enum<T>> String toSqlName(final T value) {
    return value.name().toLowerCase();
  }

  /**
   * Generate a string fragment that can be put in the IN clause of a SQL statement. eg. column IN
   * (value1, value2)
   *
   * @param values to encode
   * @param <T> enum type
   * @return "'value1', 'value2', 'value3'"
   */
  public static <T extends Enum<T>> String toSqlInFragment(final Iterable<T> values) {
    return StreamSupport.stream(values.spliterator(), false).map(Sqls::toSqlName).map(Names::singleQuote)
        .collect(Collectors.joining(",", "(", ")"));
  }

}
