/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
