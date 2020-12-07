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

import java.text.Normalizer;

public class Names {

  public static final String NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN = "[^\\p{Alnum}_]";

  /**
   * Converts any UTF8 string to a string with only alphanumeric and _ characters.
   *
   * @param s string to convert
   * @return cleaned string
   */
  public static String toAlphanumericAndUnderscore(String s) {
    return Normalizer.normalize(s, Normalizer.Form.NFKD)
        .replaceAll("\\p{M}", "")
        .replaceAll("\\s+", "_")
        .replaceAll(NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN, "_");
  }

  /**
   * Concatenate Strings together, but handles the case where the first string is already quoted
   *
   * @param name Quoted or Unquoted name to append more characters to
   * @param suffix additional string to concatenate
   * @return name and suffix concatenated together
   */
  public static String concatQuotedNames(String name, String suffix) {
    if (name.endsWith("\"")) {
      return name.substring(0, name.length() - 1) + suffix + "\"";
    } else {
      return name + suffix;
    }
  }

}
