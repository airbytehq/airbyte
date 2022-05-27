/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.string;

import com.google.common.collect.Lists;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class StringsTest {

  private static class JoinClass {

    private final int id;

    public JoinClass(final int id) {
      this.id = id;
    }

    @Override
    public String toString() {
      return "id = " + id;
    }

  }

  @Test
  void testJoin() {
    Assertions.assertEquals(
        "1, 2, 3, 4, 5",
        Strings.join(Lists.newArrayList(1, 2, 3, 4, 5), ", "));

    Assertions.assertEquals(
        "id = 1, id = 2, id = 3",
        Strings.join(Lists.newArrayList(new JoinClass(1), new JoinClass(2), new JoinClass(3)), ", "));
  }

}
