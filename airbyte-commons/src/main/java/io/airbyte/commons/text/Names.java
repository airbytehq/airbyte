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

import com.google.common.base.Preconditions;
import java.text.Normalizer;

public class Names {

  public static final String NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN = "[^\\p{Alnum}_]";

  /**
   * Converts any UTF8 string to a string with only alphanumeric and _ characters without preserving
   * accent characters.
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

  public static String doubleQuote(String value) {
    return internalQuote(value, '"');
  }

  public static String singleQuote(String value) {
    return internalQuote(value, '\'');
  }

  private static String internalQuote(final String value, final char quoteChar) {
    Preconditions.checkNotNull(value);

    boolean startsWithChar = value.charAt(0) == quoteChar;
    boolean endsWithChar = value.charAt(value.length() - 1) == quoteChar;

    Preconditions.checkState(startsWithChar == endsWithChar, "Invalid value: %s", value);

    if (startsWithChar) {
      return value;
    } else {
      return String.format("%c%s%c", quoteChar, value, quoteChar);
    }
  }

}
