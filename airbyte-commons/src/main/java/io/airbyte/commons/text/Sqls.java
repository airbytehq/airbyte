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
