/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.text;

import static io.airbyte.commons.text.Sqls.toSqlName;

import com.google.common.collect.Lists;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class SqlsTest {

  enum E1 {
    VALUE_1,
    VALUE_TWO,
    value_three,
  }

  @Test
  void testToSqlName() {
    Assertions.assertEquals("value_1", toSqlName(E1.VALUE_1));
    Assertions.assertEquals("value_two", toSqlName(E1.VALUE_TWO));
    Assertions.assertEquals("value_three", toSqlName(E1.value_three));
  }

  @Test
  void testInFragment() {
    Assertions.assertEquals("('value_two','value_three')", Sqls.toSqlInFragment(Lists.newArrayList(E1.VALUE_TWO, E1.value_three)));
  }

}
